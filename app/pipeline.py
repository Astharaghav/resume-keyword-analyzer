"""
pipeline.py
NLP processing pipeline: tokenise → remove stopwords → TF-IDF vectorisation.
Designed to be stateless — call extract_keywords() directly.
"""

import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer


# Common English stopwords (inline — no NLTK download needed)
STOPWORDS = {
    'a','an','the','and','or','but','in','on','at','to','for','of','with',
    'by','from','as','is','are','was','were','be','been','being','have',
    'has','had','do','does','did','will','would','could','should','may',
    'might','shall','can','need','dare','ought','used','i','me','my',
    'myself','we','our','ours','ourselves','you','your','yours','yourself',
    'yourselves','he','him','his','himself','she','her','hers','herself',
    'it','its','itself','they','them','their','theirs','themselves','what',
    'which','who','whom','this','that','these','those','am','into','through',
    'during','before','after','above','below','between','each','few','more',
    'most','other','some','such','no','not','only','own','same','than',
    'too','very','s','t','just','don','should','now','d','ll','m','o','re',
    'about','also','any','both','even','ever','here','how','however',
    'if','like','make','many','much','never','new','next','out','over',
    'same','so','still','then','there','throughout','together','under',
    'until','up','use','used','using','when','where','while','who','why',
    'within','without','yet'
}


def tokenise(text):
    """
    Split text into clean word tokens.
    Removes numbers, punctuation, and short tokens (< 2 chars).
    """
    # Remove numbers and punctuation
    text = re.sub(r'\d+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Split and filter
    tokens = [
        t.strip().lower()
        for t in text.split()
        if len(t.strip()) > 2 and t.strip().lower() not in STOPWORDS
    ]
    return tokens


def extract_keywords(text, top_n=30):
    """
    Extract the top N keywords from a text using TF-IDF.

    Parameters:
        text  : cleaned text string
        top_n : number of keywords to return (default 30)

    Returns:
        list of (keyword, score) tuples, sorted by score descending
    """
    if not text or len(text.split()) < 5:
        return []

    # Use TF-IDF on the single document
    # max_features limits vocabulary size
    vectorizer = TfidfVectorizer(
        max_features=500,
        ngram_range=(1, 2),       # unigrams + bigrams (e.g. "machine learning")
        stop_words='english',
        min_df=1,
        sublinear_tf=True         # apply log normalisation to term frequency
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # Zip and sort by score
        keyword_scores = [
            (word, round(float(score), 4))
            for word, score in zip(feature_names, scores)
            if score > 0
        ]
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        return keyword_scores[:top_n]

    except Exception:
        # Fallback: simple word frequency
        tokens = tokenise(text)
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        total = sum(freq.values()) or 1
        return [(w, round(c / total, 4)) for w, c in sorted_freq[:top_n]]


def get_keyword_set(text, top_n=30):
    """
    Returns just the keyword strings (no scores) as a set.
    Used for quick membership checks in scorer.py.
    """
    return {kw for kw, _ in extract_keywords(text, top_n)}


if __name__ == "__main__":
    sample = """
    python developer with experience in machine learning flask rest api
    pandas numpy scikit-learn data analysis sql database postgresql git github
    agile development object oriented programming debugging problem solving
    """
    kws = extract_keywords(sample, top_n=15)
    print("Top keywords:")
    for kw, score in kws:
        print(f"  {kw:<30} {score:.4f}")
