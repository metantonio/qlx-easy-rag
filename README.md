# QLX Easy-RAG 🚀

Easy-RAG is a multi-user Retrieval-Augmented Generation (RAG) system designed to create personal knowledge bases from uploaded documents. It features a premium, modern dark-themed UI and uses state-of-the-art embedding models to provide accurate, context-aware answers.

## ✨ Key Features

- **Multi-User Isolation**: Each user gets their own dedicated knowledge base and vector space.
- **Advanced Embeddings**: Integrated with **Qwen3-VL-Embedding-2B** for high-performance text and multimodal representations.
- **RESTful API**: Built with FastAPI, following modern web standards.
- **Vector Search**: High-performance retrieval using Qdrant.
- **LLM Integration**: Seamlessly connects to Ollama or vLLM using the OpenAI-compatible protocol.
- **Premium UI**: Stunning dark-mode interface with smooth animations and intuitive design.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Vector Database**: Qdrant
- **LLM Provider**: Ollama / vLLM
- **Embeddings**: Qwen3-VL (Transformers)
- **Database**: SQLite (for user & metadata management)
- **Frontend**: Vanilla HTML / CSS / JavaScript

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.10+**
- **Qdrant**: (Choose one option)
  - **Local Mode (Default)**: No installation needed. QLX Easy-RAG will automatically use local storage via `QDRANT_PATH` in `.env`.
  - **Docker Mode**: If you prefer Docker, clear `QDRANT_PATH` in `.env` and run:
    ```bash
    docker run -p 6333:6333 qdrant/qdrant
    ```
- **Ollama**: Running on port `11434` with your preferred model (e.g., `llama3`)
  ```bash
  ollama run llama3
  ```

### 2. Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup environment variables:
   Generate your `.env` from the provided example:
   ```bash
   cp .env.example .env
   ```

### 3. Running the Application

Start the FastAPI server:
```bash
python -m backend.main
```

Access the web interface at: **`http://localhost:8000`**

## 📂 Project Structure

- `backend/`: FastAPI application, models, and RAG services.
- `frontend/`: Premium web interface assets.
- `data/`: Local storage for SQLite DB and document uploads.
- `qwen3_vl.md`: Technical guide for the embedding model.

## 📜 Requirements

The project follows the technical requirements specified in `Technical_requirements.txt`, ensuring a robust, scalable, and user-friendly RAG experience.
