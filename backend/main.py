from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import shutil

from .core.config import settings
from .core.database import get_db, engine, Base
from .models import models
from .services.document_processor import doc_processor
from .services.vector_db import vector_db
from .services.llm import llm_service

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Easy-RAG API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return {"message": "Easy-RAG API is running"}

# Simplified Auth/User registration for this demo
@app.post("/register")
def register(username: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        return db_user
    new_user = models.User(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/upload")
async def upload_document(
    user_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    upload_dir = f"data/uploads/{user_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_doc = models.Document(filename=file.filename, file_path=file_path, user_id=user_id)
    db.add(db_doc)
    db.commit()
    
    # Process for KB
    chunks_count = doc_processor.process_file(file_path, user_id)
    
    return {"message": "File uploaded and processed", "chunks": chunks_count}

@app.get("/query")
async def query_kb(user_id: int, q: str):
    # RAG Flow
    # 1. Search vector DB
    search_results = vector_db.search(user_id, q)
    
    if not search_results:
        return {"answer": "No relevant information found in your knowledge base."}
    
    # 2. Construct context
    context = "\n---\n".join([r["text"] for r in search_results])
    
    # 3. Generate response
    answer = llm_service.generate_response(q, context)
    
    return {
        "answer": answer,
        "sources": [r["metadata"].get("source") for r in search_results]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
