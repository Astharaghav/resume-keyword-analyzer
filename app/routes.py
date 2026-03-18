"""
routes.py
3 REST API endpoints:
  POST /api/upload   — upload resume + JD text, get match score
  POST /api/analyse  — analyse pre-extracted text directly
  GET  /api/health   — health check

All responses are JSON. Errors return structured JSON with 'error' key.
"""

from flask import Blueprint, request, jsonify
from app.cleaner import extract_and_clean
from app.scorer  import calculate_match_score, get_improvement_tips

api = Blueprint('api', __name__)


@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status":  "ok",
        "service": "resume-keyword-analyzer",
        "version": "1.0.0"
    }), 200


@api.route('/upload', methods=['POST'])
def upload():
    """
    Upload resume and JD as files.

    Request (multipart/form-data):
        resume : file (.pdf, .docx, .txt)
        jd     : file (.pdf, .docx, .txt)

    Response (JSON):
        score, verdict, matched, missing, tips, resume_keywords, jd_keywords
    """
    # Validate request
    if 'resume' not in request.files:
        return jsonify({"error": "Missing 'resume' file in request"}), 400
    if 'jd' not in request.files:
        return jsonify({"error": "Missing 'jd' file in request"}), 400

    resume_file = request.files['resume']
    jd_file     = request.files['jd']

    if resume_file.filename == '':
        return jsonify({"error": "Resume file is empty"}), 400
    if jd_file.filename == '':
        return jsonify({"error": "JD file is empty"}), 400

    # Extract and clean text
    resume_bytes = resume_file.read()
    jd_bytes     = jd_file.read()

    resume_text, resume_status = extract_and_clean(resume_bytes, resume_file.filename)
    jd_text,     jd_status     = extract_and_clean(jd_bytes,     jd_file.filename)

    if resume_status != "ok":
        return jsonify({"error": f"Resume processing failed: {resume_status}"}), 422
    if jd_status != "ok":
        return jsonify({"error": f"JD processing failed: {jd_status}"}), 422

    # Score
    result = calculate_match_score(resume_text, jd_text)
    result["tips"] = get_improvement_tips(result.get("missing", []))

    return jsonify(result), 200


@api.route('/analyse', methods=['POST'])
def analyse():
    """
    Analyse pre-extracted text directly (no file upload).

    Request (JSON):
        {
            "resume_text": "...",
            "jd_text":     "..."
        }

    Response (JSON):
        score, verdict, matched, missing, tips, resume_keywords, jd_keywords
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    resume_text = data.get("resume_text", "").strip()
    jd_text     = data.get("jd_text", "").strip()

    if not resume_text:
        return jsonify({"error": "Missing 'resume_text' in request body"}), 400
    if not jd_text:
        return jsonify({"error": "Missing 'jd_text' in request body"}), 400

    if len(resume_text.split()) < 10:
        return jsonify({"error": "resume_text is too short (minimum 10 words)"}), 422
    if len(jd_text.split()) < 5:
        return jsonify({"error": "jd_text is too short (minimum 5 words)"}), 422

    # Clean the raw text
    from app.cleaner import extract_text_from_string
    resume_clean = extract_text_from_string(resume_text)
    jd_clean     = extract_text_from_string(jd_text)

    # Score
    result = calculate_match_score(resume_clean, jd_clean)
    result["tips"] = get_improvement_tips(result.get("missing", []))

    return jsonify(result), 200


@api.route('/report', methods=['POST'])
def report():
    """
    Generate a detailed text report from analysis results.

    Request (JSON) — same as /analyse:
        { "resume_text": "...", "jd_text": "..." }

    Response (JSON):
        report (str) — formatted text report
        + all fields from /analyse
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    resume_text = data.get("resume_text", "").strip()
    jd_text     = data.get("jd_text", "").strip()

    if not resume_text or not jd_text:
        return jsonify({"error": "Both 'resume_text' and 'jd_text' are required"}), 400

    from app.cleaner import extract_text_from_string
    resume_clean = extract_text_from_string(resume_text)
    jd_clean     = extract_text_from_string(jd_text)

    result = calculate_match_score(resume_clean, jd_clean)
    tips   = get_improvement_tips(result.get("missing", []))

    # Build human-readable report
    lines = [
        "=" * 50,
        "  RESUME KEYWORD ANALYSIS REPORT",
        "=" * 50,
        f"  Match Score : {result['score']}%",
        f"  Verdict     : {result['verdict']}",
        f"  Matched     : {result['total_matched']} / {result['total_jd_kws']} JD keywords",
        "",
        "  MATCHED KEYWORDS:",
        "  " + ", ".join(result['matched'][:15]) if result['matched'] else "  None",
        "",
        "  MISSING KEYWORDS:",
        "  " + ", ".join(result['missing'][:15]) if result['missing'] else "  None",
        "",
        "  IMPROVEMENT TIPS:",
    ] + [f"  - {tip}" for tip in tips] + ["=" * 50]

    result["report"] = "\n".join(lines)
    result["tips"]   = tips
    return jsonify(result), 200
