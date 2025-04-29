import os
import uuid
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from docx import Document
from core.generate import get_embedding
from core.config import COLLECTION_NAME, QDRANT_API_KEY, QDRANT_CLUSTER_URL

# Create client here instead of importing
client = QdrantClient(
    url=QDRANT_CLUSTER_URL,
    api_key=QDRANT_API_KEY
)


def embed_final_rfp(file_path):
    """
    Load a final RFP draft from DOCX, create embeddings for each paragraph, and upload to Qdrant.
    """
    # Load final draft
    doc = Document(file_path)

    points = []
    for para in doc.paragraphs:
        question = para.text.strip()
        if not question:
            continue  # skip empty lines

        vector = get_embedding(question, use_openai=False)

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"source": os.path.basename(file_path)}
        )
        points.append(point)

    # Upload all points
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Final draft '{file_path}' vectorized and uploaded to Qdrant.")


def embed_text(text: str, model: str = "nomic-embed-text"):
    """
    Embed text locally using Ollama.
    """
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": text}
    )
    return response.json()["embedding"]
