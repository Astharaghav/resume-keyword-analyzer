# resume-keyword-analyzer
NLP pipeline that matches resumes to job descriptions — TF-IDF keyword extraction, 240x faster than manual
# Resume Keyword Analyzer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/astha-raghav/resume-keyword-analyzer/blob/main/notebooks/Resume_Keyword_Analyzer_Colab.ipynb)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![NLP](https://img.shields.io/badge/NLP-TF--IDF-orange)
![Speedup](https://img.shields.io/badge/Speedup-240x-brightgreen)

An NLP-powered tool that compares a resume against a job description using TF-IDF keyword extraction and returns a match score, matched keywords, missing keywords, and improvement tips.

**Key result:** Reduces manual resume screening from 15–20 minutes to under 5 seconds — a 240× speedup.

---

## Results

| Metric | Value |
|---|---|
| Processing time | < 5 seconds per analysis |
| Manual equivalent | 15–20 minutes |
| Speedup | ~240× |
| Documents tested | 20 real-world resumes |
| Edge cases handled | Malformed PDFs, encoding errors, missing sections, empty inputs |

---

## How It Works

```
Resume / JD text
   → clean_text()        remove noise, URLs, emails, special chars
   → extract_keywords()  TF-IDF on unigrams + bigrams
   → calculate_match()   intersection of keyword sets
   → score               matched / total JD keywords × 100
   → report              score, verdict, matched, missing, tips
```

---

## API Endpoints

| Method | Endpoint | Input | Output |
|---|---|---|---|
| GET | `/api/health` | — | `{ status: "ok" }` |
| POST | `/api/upload` | multipart: `resume` + `jd` files | match report JSON |
| POST | `/api/analyse` | JSON: `resume_text`, `jd_text` | match report JSON |
| POST | `/api/report` | JSON: `resume_text`, `jd_text` | match report + formatted text |

### Sample Response

```json
{
  "score": 72.5,
  "verdict": "Strong Match",
  "matched": ["python", "flask", "machine learning", "sql", "git"],
  "missing": ["django", "docker", "postgresql"],
  "total_jd_kws": 18,
  "total_matched": 13,
  "tips": [
    "Consider adding 'django' to your resume if you have this skill.",
    "Consider adding 'docker' to your resume if you have this skill."
  ]
}
```

---

## Project Structure

```
resume-keyword-analyzer/
├── app/
│   ├── __init__.py
│   ├── cleaner.py       # text extraction + noise removal
│   ├── pipeline.py      # tokenisation + TF-IDF keyword extraction
│   ├── scorer.py        # keyword matching + score calculation
│   └── routes.py        # 4 Flask REST API endpoints
├── notebooks/
│   └── Resume_Keyword_Analyzer_Colab.ipynb   # run on Google Colab
├── tests/
│   └── test_pipeline.py  # unit tests for all modules
├── sample_docs/           # sample PDFs/TXTs for testing
├── run.py                 # Flask app entry point
└── requirements.txt
```

---

## How to Run

### Option A: Google Colab (recommended — no setup needed)
Click the **Open in Colab** badge at the top. Run all cells.

### Option B: Run locally

```bash
git clone https://github.com/astha-raghav/resume-keyword-analyzer
cd resume-keyword-analyzer
pip install -r requirements.txt
python run.py
```

Server starts at `http://localhost:5000`

### Test with Postman or curl

```bash
# Health check
curl http://localhost:5000/api/health

# Analyse text directly
curl -X POST http://localhost:5000/api/analyse \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "python flask machine learning sql pandas git", "jd_text": "python django sql machine learning data analysis git agile"}'

# Upload files
curl -X POST http://localhost:5000/api/upload \
  -F "resume=@my_resume.txt" \
  -F "jd=@job_description.txt"
```

### Run tests

```bash
python tests/test_pipeline.py
```

---

## Edge Cases Handled

| Edge Case | How handled |
|---|---|
| Malformed PDF | `try/except` around PDF extraction, returns empty string |
| Encoding errors | `encode('utf-8', errors='ignore')` on all input |
| Empty document | Checked before processing, returns 422 with message |
| Very short text | Minimum word count validation (10 words resume, 5 JD) |
| Special characters | Regex strips non-alphanumeric characters |
| Phone numbers | Regex pattern removes all phone formats |
| URLs and emails | Specific regex patterns for each |

---

## Key Learnings

1. **TF-IDF on a single document** still works as a keyword ranker because `sublinear_tf=True` + `stop_words='english'` surfaces domain-specific terms over generic words.
2. **Bigrams** (`ngram_range=(1,2)`) significantly improve matching — "machine learning" as a bigram matches JD requirements better than "machine" and "learning" separately.
3. **Fit on train only** — in a multi-document setting, the vectorizer must be fit on the corpus, not individual documents. For single-document keyword extraction, fit+transform on the same document is intentional and correct.

---

## Author

**Astha Raghav** — [LinkedIn](https://linkedin.com/in/astha-raghav) | [GitHub](https://github.com/astha-raghav)  
Research: Co-authored Scopus-indexed paper on applied ML (IMACSI 2025)
