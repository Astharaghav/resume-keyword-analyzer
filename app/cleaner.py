"""
cleaner.py
Handles raw document ingestion and noise removal.
Supports PDF, DOCX, and plain TXT files.
Deals with real-world edge cases: malformed encoding, empty sections, special characters.
"""

import re
import string


def extract_text_from_string(raw_text):
    """
    Clean a raw text string — remove noise, fix encoding issues,
    normalise whitespace. Works on any text regardless of source.
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    # Decode common encoding artifacts
    text = raw_text
    text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', ' ', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', ' ', text)

    # Remove phone numbers
    text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', ' ', text)

    # Remove special characters but keep letters, numbers, spaces
    text = re.sub(r'[^a-zA-Z0-9\s\-\/]', ' ', text)

    # Collapse multiple whitespace into single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip().lower()

    return text


def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Extract text from PDF file bytes.
    Handles malformed PDFs gracefully — returns empty string on failure.
    """
    try:
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n".join(pages)
    except Exception:
        return ""


def extract_text_from_docx_bytes(docx_bytes):
    """
    Extract text from DOCX file bytes.
    Handles missing/corrupt documents gracefully.
    """
    try:
        import docx
        import io
        doc = docx.Document(io.BytesIO(docx_bytes))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return ""


def extract_and_clean(file_bytes, filename):
    """
    Master function — detects file type, extracts text, cleans it.

    Parameters:
        file_bytes : raw bytes of the uploaded file
        filename   : original filename (used to detect type)

    Returns:
        clean_text (str) : cleaned, lowercased text ready for NLP
        status     (str) : 'ok' or error description
    """
    filename_lower = filename.lower()

    # Extract raw text based on file type
    if filename_lower.endswith('.pdf'):
        raw = extract_text_from_pdf_bytes(file_bytes)
        if not raw.strip():
            return "", "PDF text extraction failed — file may be image-based or corrupted"

    elif filename_lower.endswith('.docx'):
        raw = extract_text_from_docx_bytes(file_bytes)
        if not raw.strip():
            return "", "DOCX extraction failed — file may be corrupted"

    elif filename_lower.endswith('.txt'):
        try:
            raw = file_bytes.decode('utf-8', errors='ignore')
        except Exception:
            return "", "TXT decoding failed"

    else:
        return "", f"Unsupported file type: {filename}. Supported: .pdf, .docx, .txt"

    if not raw or len(raw.strip()) < 20:
        return "", "Document appears to be empty or too short to analyse"

    clean = extract_text_from_string(raw)

    if len(clean.split()) < 10:
        return "", "Extracted text too short — check document content"

    return clean, "ok"


if __name__ == "__main__":
    # Quick test with plain text
    sample = "Hello! My name is Astha. I know Python, Flask, and machine learning."
    result = extract_text_from_string(sample)
    print(f"Input : {sample}")
    print(f"Output: {result}")
