# chunker.py
import os 
from dotenv import load_dotenv

load_dotenv()

MAX_CHARS = int(os.getenv("MAX_CHARS", 300))
OVERLAP = int(os.getenv("OVERLAP", 20))


def chunk_documents(docs, max_char=MAX_CHARS, overlap=OVERLAP):
    """
    Breaks long documents into smaller overlapping chunks.
    Returns a list of dicts with text + metadata for traceability.
    """
    chunked_docs_with_meta = []
    
    for doc_id, doc in enumerate(docs):
        start = 0
        doc_len = len(doc)

        while start < doc_len:
            end = min(start + max_char, doc_len)
            chunk = doc[start:end]

            # Save chunk with metadata
            chunked_docs_with_meta.append({
                "text": chunk,
                "metadata": {
                    "source": f"doc_{doc_id}.txt",
                    "start": start,
                    "end": end
                }
            })

            start += max_char - overlap  # move forward with overlap

    return chunked_docs_with_meta
