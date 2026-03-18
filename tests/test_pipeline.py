"""
tests/test_pipeline.py
Unit tests for cleaner, scorer, and pipeline modules.
Run: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestCleaner:

    def test_basic_cleaning(self):
        from cleaner import clean_text
        result = clean_text("Hello WORLD!!! Check this: https://google.com")
        assert "hello" in result
        assert "world" in result
        assert "https" not in result
        assert "!!!" not in result

    def test_email_removed(self):
        from cleaner import clean_text
        result = clean_text("Contact: john@example.com for details")
        assert "@" not in result
        assert "example" not in result

    def test_phone_removed(self):
        from cleaner import clean_text
        result = clean_text("Call me at +91 9876543210 anytime")
        assert "9876543210" not in result

    def test_empty_input_returns_empty(self):
        from cleaner import clean_text
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_tokenise_filters_short(self):
        from cleaner import tokenise
        tokens = tokenise("a bb ccc dddd")
        assert "a" not in tokens
        assert "bb" in tokens

    def test_tokenise_filters_digits(self):
        from cleaner import tokenise
        tokens = tokenise("python 123 machine learning 456")
        assert "123" not in tokens
        assert "456" not in tokens
        assert "python" in tokens

    def test_bigrams_generated(self):
        from cleaner import get_ngrams
        tokens  = ["machine", "learning", "python"]
        bigrams = get_ngrams(tokens, 2)
        assert "machine_learning" in bigrams
        assert "learning_python" in bigrams

    def test_encoding_handled(self):
        from cleaner import clean_text
        result = clean_text("Caf\u00e9 skills and na\u00efve experience")
        assert isinstance(result, str)
        assert len(result) > 0


class TestScorer:

    def test_returns_match_score(self):
        from scorer import score_resume_against_jd
        resume = "python machine learning data analysis scikit-learn pandas numpy sql flask rest api"
        jd     = "python developer machine learning data analysis sql rest api"
        result = score_resume_against_jd(resume, jd)
        assert "match_score" in result
        assert 0 <= result["match_score"] <= 100

    def test_perfect_match(self):
        from scorer import score_resume_against_jd
        text   = "python data analysis machine learning scikit-learn sql pandas"
        result = score_resume_against_jd(text, text)
        assert result["match_score"] == 100.0

    def test_zero_match(self):
        from scorer import score_resume_against_jd
        resume = "cooking baking gardening painting music"
        jd     = "python tensorflow deep learning neural networks gpu"
        result = score_resume_against_jd(resume, jd)
        assert result["match_score"] < 20

    def test_matched_keywords_in_resume(self):
        from scorer import score_resume_against_jd
        resume = "experienced python developer with machine learning skills"
        jd     = "python developer machine learning required"
        result = score_resume_against_jd(resume, jd)
        matched = list(result["matched_keywords"].keys())
        assert any("python" in k for k in matched)

    def test_recommendation_returned(self):
        from scorer import score_resume_against_jd
        result = score_resume_against_jd("python flask sql", "python sql flask rest")
        assert "recommendation" in result
        assert len(result["recommendation"]) > 0

    def test_empty_inputs_return_error(self):
        from scorer import score_resume_against_jd
        result = score_resume_against_jd("", "some jd text here")
        assert "error" in result


class TestPipeline:

    def test_pipeline_returns_success(self):
        from pipeline import run_pipeline
        resume = "Python developer with machine learning and data analysis experience. Flask REST API SQL"
        jd     = "Python developer needed. Machine learning, data analysis, SQL, REST API required."
        result = run_pipeline(resume, jd)
        assert result["status"] == "success"
        assert "match_score" in result

    def test_pipeline_has_timing(self):
        from pipeline import run_pipeline
        result = run_pipeline(
            "python machine learning developer sql",
            "python developer machine learning sql required"
        )
        assert "processing_time_sec" in result
        assert result["processing_time_sec"] < 5.0

    def test_pipeline_word_counts(self):
        from pipeline import run_pipeline
        result = run_pipeline(
            "python machine learning data analysis sql pandas numpy",
            "python developer machine learning data analysis sql"
        )
        assert result["resume_word_count"] > 0
        assert result["jd_word_count"] > 0

    def test_pipeline_rejects_short_text(self):
        from pipeline import run_pipeline
        result = run_pipeline("hi", "python machine learning developer sql rest api")
        assert "error" in result

    def test_pipeline_speed_under_5_seconds(self):
        import time
        from pipeline import run_pipeline
        resume = " ".join(["python machine learning data analysis sql flask rest api pandas numpy scikit-learn"] * 20)
        jd     = " ".join(["python developer machine learning data analysis sql rest api required"] * 10)
        start  = time.time()
        result = run_pipeline(resume, jd)
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Pipeline too slow: {elapsed:.2f}s"
        assert result["status"] == "success"


if __name__ == "__main__":
    import sys
    # Run manually without pytest
    test_classes = [TestCleaner, TestScorer, TestPipeline]
    passed = 0
    failed = 0
    for cls in test_classes:
        obj = cls()
        for method in [m for m in dir(obj) if m.startswith('test_')]:
            try:
                getattr(obj, method)()
                print(f"  PASS  {cls.__name__}.{method}")
                passed += 1
            except Exception as e:
                print(f"  FAIL  {cls.__name__}.{method} — {e}")
                failed += 1
    print(f"\n{passed} passed, {failed} failed")
