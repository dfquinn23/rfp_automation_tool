import requests
from core.config import OLLAMA_EMBEDDING_MODEL


def embed_text(text: str, model: str = OLLAMA_EMBEDDING_MODEL):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": text}
    )
    return response.json()["embedding"]
