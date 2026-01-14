import os
from .vector_db import vector_db

class DocumentProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str, user_id: int):
        content = ""
        
        # Check if file is PDF
        if file_path.lower().endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
                print(f"Extracted {len(content)} characters from PDF: {file_path}")
            except Exception as e:
                print(f"Error reading PDF {file_path}: {e}")
                return 0
        else:
            # List of common encodings to try for text files
            encodings = ["utf-8", "latin-1", "cp1252"]
            for enc in encodings:
                try:
                    with open(file_path, "r", encoding=enc) as f:
                        content = f.read()
                    break # Success
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            if not content:
                # Fallback: read with utf-8 and ignore errors
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    return 0
        
        chunks = self.chunk_text(content)
        metadatas = [{"source": os.path.basename(file_path)} for _ in chunks]
        
        vector_db.upsert_documents(user_id, chunks, metadatas)
        return len(chunks)

    def chunk_text(self, text: str):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return chunks

doc_processor = DocumentProcessor()
