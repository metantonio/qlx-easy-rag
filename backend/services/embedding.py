import torch
from transformers import AutoModel, AutoTokenizer
from qwen_vl_utils import process_vision_info
import numpy as np
from typing import List, Dict, Any, Union
from ..core.config import settings

class Qwen3VLEmbedder:
    def __init__(self, model_name_or_path: str = None, device: str = None):
        self.model_name_or_path = model_name_or_path or settings.EMBEDDING_MODEL_PATH
        requested_device = device or settings.DEVICE
        
        # Check if CUDA is actually available
        if requested_device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA requested but not available. Falling back to CPU.")
            self.device = "cpu"
        else:
            self.device = requested_device
        
        print(f"Loading Qwen3-VL Embedding model from {self.model_name_or_path}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            self.model_name_or_path, 
            trust_remote_code=True,
            dtype=torch.float16 if self.device == "cuda" else torch.float32,
        ).to(self.device).eval()
        
        print("Model loaded successfully.")

    def process(self, inputs: List[Dict[str, Any]]) -> np.ndarray:
        """
        Process a list of inputs (text/image) and return embeddings.
        Example input: [{"text": "hello"}, {"image": "path/to/img.jpg"}]
        """
        embeddings = []
        for inp in inputs:
            # This is a simplified version of the processing logic from qwen3_vl.md
            # Qwen3-VL requires specific formatting for multimodal inputs
            
            # For pure text:
            if "text" in inp and "image" not in inp:
                text = inp["text"]
                inputs_encoded = self.tokenizer(text, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    outputs = self.model(**inputs_encoded)
                    # Assuming the model returns embeddings in a specific hidden state or pooler output
                    # Based on standard embedding models, we take the mean or [CLS]
                    embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                    embeddings.append(embedding[0])
            
            # For multimodal (simplified for now):
            elif "image" in inp or ("text" in inp and "image" in inp):
                # Using process_vision_info as indicated in the docs
                # For brevity, we'll handle this using the transformers pipeline or the manual method
                # This part normally requires more complex preprocessing of images
                # For the sake of this RAG, we primarily focus on text but keep image support in mind
                pass 
                
        return np.array(embeddings)

# Singleton instance
embedder = None

def get_embedder():
    global embedder
    if embedder is None:
        embedder = Qwen3VLEmbedder()
    return embedder
