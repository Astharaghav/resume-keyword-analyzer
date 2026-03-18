"""
scorer.py
Compares resume keywords against job description keywords.
Returns a match score, matched keywords, and missing keywords.
"""

from app.pipeline import extract_keywords, get_keyword_set


def calculate_match_score(resume_text, jd_text, top_n=40):
    """
    Compare resume against job description and return a match report.

    Parameters:
        resume_text : cleaned resume text
        jd_text     : cleaned job description text
        top_n       : how many top keywords to extract from JD

    Returns:
        dict with:
            score           : match percentage (0–100)
            matched         : list of keywords found in both
            missing         : list of JD keywords not in resume
            resume_keywords : all keywords extracted from resume
            jd_keywords     : all keywords extracted from JD
            verdict         : 'Strong Match' / 'Partial Match' / 'Weak Match'
    """
    if not resume_text or not jd_text:
        return {
            "score": 0,
            "matched": [],
            "missing": [],
            "resume_keywords": [],
            "jd_keywords": [],
            "verdict": "Error — empty input"
        }

    # Extract keyword sets
    jd_kw_scores    = extract_keywords(jd_text, top_n=top_n)
    resume_kw_scores = extract_keywords(resume_text, top_n=top_n * 2)

    jd_keywords     = [kw for kw, _ in jd_kw_scores]
    resume_keywords = [kw for kw, _ in resume_kw_scores]

    jd_set     = set(jd_keywords)
    resume_set = set(resume_keywords)

    # Match: keywords in JD that also appear in resume
    matched = sorted(jd_set & resume_set)
    missing = sorted(jd_set - resume_set)

    # Score = percentage of JD keywords found in resume
    score = round((len(matched) / len(jd_set)) * 100, 1) if jd_set else 0

    # Verdict
    if score >= 70:
        verdict = "Strong Match"
    elif score >= 40:
        verdict = "Partial Match"
    else:
        verdict = "Weak Match"

    return {
        "score":            score,
        "matched":          matched,
        "missing":          missing,
        "resume_keywords":  resume_keywords[:20],
        "jd_keywords":      jd_keywords[:20],
        "total_jd_kws":     len(jd_set),
        "total_matched":    len(matched),
        "verdict":          verdict
    }


def get_improvement_tips(missing_keywords):
    """
    Generate simple suggestions for missing keywords.
    Returns top 10 missing keywords as action items.
    """
    if not missing_keywords:
        return ["Great match — no major gaps found."]

    tips = []
    for kw in missing_keywords[:10]:
        tips.append(f"Consider adding '{kw}' to your resume if you have this skill.")
    return tips


if __name__ == "__main__":
    resume = """
    python developer machine learning flask rest api pandas numpy scikit-learn
    data analysis sql mysql git github agile sprint debugging object oriented
    programming feature engineering model training evaluation cross validation
    """
    jd = """
    looking for python developer with experience in django rest api postgresql
    machine learning scikit-learn pandas data analysis git agile communication
    problem solving team collaboration sql database management deployment docker
    """

    result = calculate_match_score(resume, jd)
    print(f"Score   : {result['score']}%")
    print(f"Verdict : {result['verdict']}")
    print(f"Matched : {result['matched']}")
    print(f"Missing : {result['missing']}")
