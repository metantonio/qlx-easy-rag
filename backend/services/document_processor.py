import os
from .vector_db import vector_db

class DocumentProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str, user_id: int):
        # Extremely basic text extraction for demo purposes. 
        # In a real app, use PyPDF2 or similar for PDFs.
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
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
