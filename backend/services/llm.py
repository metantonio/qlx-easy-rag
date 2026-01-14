from openai import OpenAI
from ..core.config import settings

class LLMService:
    def __init__(self):
        # We use the OpenAI-compatible client for both Ollama and vLLM
        self.client = OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.OPENAI_API_KEY
        )
        self.model = settings.LLM_MODEL

    def generate_response(self, prompt: str, context: str = ""):
        system_prompt = (
            "You are a helpful assistant. Use the provided context to answer the user's question. "
            "If the answer is not in the context, say you don't know based on the knowledge base."
        )
        
        full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content

llm_service = LLMService()
