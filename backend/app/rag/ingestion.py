"""
PDF ingestion pipeline.
Reads artemis2-reference-guide.pdf page-by-page using PyMuPDF,
cleans text, and splits into chunks using RecursiveCharacterTextSplitter.
"""

import logging
import re
from pathlib import Path

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Chunking configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 80
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def _clean_text(text: str) -> str:
    """Strip extra whitespace and control characters."""
    # Remove control characters (keep newline and tab)
    text = "".join(c for c in text if c in ("\n", "\t") or ord(c) >= 32)
    # Collapse multiple spaces/tabs into single space
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ingest_pdf(pdf_path: str) -> list[dict]:
    """
    Read a PDF file page-by-page, clean text, and split into chunks.

    Returns:
        List of dicts: {"text": str, "metadata": dict}
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
    )

    doc = fitz.open(str(path))
    total_pages = len(doc)
    all_chunks = []
    chunk_index = 0

    logger.info(f"Reading PDF: {path.name} ({total_pages} pages)")

    for page_num in range(total_pages):
        page_text = doc[page_num].get_text()
        page_text = _clean_text(page_text)

        # Skip empty pages
        if not page_text:
            continue

        # Split page text into chunks
        splits = splitter.split_text(page_text)

        for split_text in splits:
            all_chunks.append({
                "text": split_text,
                "metadata": {
                    "source_file": "artemis2-reference-guide.pdf",
                    "page_number": page_num + 1,
                    "chunk_index": chunk_index,
                },
            })
            chunk_index += 1

    doc.close()
    logger.info(f"Ingestion complete: {chunk_index} chunks from {total_pages} pages")
    return all_chunks
