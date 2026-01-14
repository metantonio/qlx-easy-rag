from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..core.config import settings
from .embedding import get_embedder
import uuid

class VectorDBService:
    def __init__(self):
        if settings.QDRANT_PATH:
            print(f"Initializing Qdrant in local storage mode at {settings.QDRANT_PATH}")
            self.client = QdrantClient(path=settings.QDRANT_PATH)
        else:
            print(f"Connecting to Qdrant server at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY
            )
        self.vector_size = 2048 # Adjust based on Qwen3-VL-Embedding-2B output size

    def ensure_user_collection(self, user_id: int):
        collection_name = f"user_{user_id}_kb"
        collections = self.client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
            )
        return collection_name

    def upsert_documents(self, user_id: int, texts: list, metadatas: list):
        collection_name = self.ensure_user_collection(user_id)
        embedder = get_embedder()
        
        # Prepare inputs for embedder
        inputs = [{"text": t} for t in texts]
        embeddings = embedder.process(inputs)
        
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=emb.tolist(),
                payload={**metadatas[i], "text": texts[i]}
            )
            for i, emb in enumerate(embeddings)
        ]
        
        self.client.upsert(collection_name=collection_name, points=points)

    def search(self, user_id: int, query: str, limit: int = 5):
        collection_name = self.ensure_user_collection(user_id)
        embedder = get_embedder()
        
        query_embedding = embedder.process([{"text": query}])[0]
        
        response = self.client.query_points(
            collection_name=collection_name,
            query=query_embedding.tolist(),
            limit=limit
        )
        
        return [
            {"text": r.payload["text"], "score": r.score, "metadata": r.payload}
            for r in response.points
        ]

vector_db = VectorDBService()
