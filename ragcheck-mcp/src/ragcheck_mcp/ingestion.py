import os
from pathlib import Path
from .db import WorkspaceDB

try:
    import pypdf
except ImportError:
    pypdf = None

def simple_chunker(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """A basic character-based sliding window chunker."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
    return chunks

def extract_text_from_pdf(file_path: Path) -> str:
    """Extracts text from a PDF file."""
    if pypdf is None:
        raise ImportError("pypdf is required to read PDF files.")
        
    text = ""
    with open(file_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def ingest_workspace(docs_dir: str, db: WorkspaceDB) -> int:
    """Reads all markdown, text, and PDF files in a directory and stores chunks in the DB."""
    supported_extensions = {".md", ".txt", ".pdf"}
    total_chunks = 0
    
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        raise FileNotFoundError(f"Directory {docs_dir} does not exist.")

    for root, _, files in os.walk(docs_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in supported_extensions:
                try:
                    if file_path.suffix.lower() == ".pdf":
                        content = extract_text_from_pdf(file_path)
                    else:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                    if not content.strip():
                        continue
                        
                    doc_id = db.insert_document(str(file_path), content, {"source": str(file_path)})
                    chunks = simple_chunker(content)
                    db.insert_chunks(doc_id, chunks)
                    total_chunks += len(chunks)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
    return total_chunks
