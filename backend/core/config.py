from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Server configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/easy_rag.db"
    
    # Vector Database (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_PATH: Optional[str] = "./data/qdrant_db" # Set this to use local storage instead of server
    
    # LLM (Ollama / vLLM)
    LLM_PROVIDER: str = "ollama"
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL: str = "llama3"
    OPENAI_API_KEY: Optional[str] = "not-needed-for-local"
    
    # Embedding Model (Qwen3-VL)
    EMBEDDING_MODEL_PATH: str = "Qwen/Qwen3-VL-Embedding-2B"
    DEVICE: str = "cpu"
    
    # Security
    SECRET_KEY: str = "yoursecretkeyhere"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
