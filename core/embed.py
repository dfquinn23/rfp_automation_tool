# CLOUD ONLY
# core/embed.py

import os
import uuid
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from core.generate import get_embedding
from core.config import (
    QDRANT_API_KEY,
    QDRANT_CLUSTER_URL,
    COLLECTION_NAME
)

# Initialize Qdrant client
client = QdrantClient(
    url=QDRANT_CLUSTER_URL,
    api_key=QDRANT_API_KEY,
)

# Recreate collection to ensure correct vector size and distance


def ensure_correct_collection():
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,  # required by text-embedding-3-small
                distance=Distance.COSINE
            )
        )
        print(
            f"[INFO] Collection '{COLLECTION_NAME}' recreated with dim=1536.")
    except Exception as e:
        print(f"[WARNING] Could not recreate collection: {e}")


def embed_final_rfp(file_path):
    """
    Load a final RFP draft from DOCX, create embeddings for each paragraph, and upload to Qdrant.
    """

    doc = Document(file_path)
    points = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue  # skip empty lines

        try:
            vector = get_embedding(text)
            point = PointStruct(
                id=str(uuid.uuid4()),
                payload={"text": text},
                vector=vector
            )
            points.append(point)
        except Exception as e:
            print(f"⚠️ Failed to embed paragraph: {e}")

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"[INFO] Uploaded {len(points)} points to Qdrant.")


# LOCAL ONLY
# import shutil
# import os
# import uuid
# import requests
# from qdrant_client import QdrantClient
# from qdrant_client.models import PointStruct
# from docx import Document
# from core.generate import get_embedding
# from core.config import COLLECTION_NAME, QDRANT_API_KEY, QDRANT_CLUSTER_URL

# # Create client here instead of importing
# client = QdrantClient(
#     url=QDRANT_CLUSTER_URL,
#     api_key=QDRANT_API_KEY
# )


# def embed_final_rfp(file_path):
#     """
#     Load a final RFP draft from DOCX, create embeddings for each paragraph, and upload to Qdrant.
#     """
#     from docx import Document
#     from core.generate import get_embedding  # if not already imported
#     from qdrant_client.models import PointStruct

#     doc = Document(file_path)
#     points = []

#     for para in doc.paragraphs:
#         question = para.text.strip()
#         if not question:
#             continue

#         vector = get_embedding(question, use_openai=False)

#         point = PointStruct(
#             id=str(uuid.uuid4()),
#             vector=vector,
#             payload={
#                 "source": os.path.basename(file_path),
#                 "answer": question
#             }
#         )
#         points.append(point)

#     client.upsert(collection_name=COLLECTION_NAME, points=points)
#     print(f"✅ Final draft '{file_path}' vectorized and uploaded to Qdrant.")


# def embed_text(text: str, model: str = "nomic-embed-text"):
#     """
#     Embed text locally using Ollama.
#     """
#     response = requests.post(
#         "http://localhost:11434/api/embeddings",
#         json={"model": model, "prompt": text}
#     )
#     return response.json()["embedding"]


# def save_final_rfp(file_path):
#     """
#     Save the finalized RFP document into the 'past_rfps/' folder.
#     """
#     dest_dir = "past_rfps"
#     os.makedirs(dest_dir, exist_ok=True)
#     dest_path = os.path.join(dest_dir, os.path.basename(file_path))
#     shutil.copy(file_path, dest_path)
#     print(f"✅ Final RFP saved to {dest_path}")
