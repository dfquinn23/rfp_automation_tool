import os
import uuid
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from core.generate import get_embedding
from dotenv import load_dotenv

# Load environment variables or Streamlit secrets
load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_CLUSTER_URL = os.getenv("QDRANT_CLUSTER_URL")
COLLECTION_NAME = "past_rfp_answers"
PAST_RFPS_DIR = "past_rfps"

client = QdrantClient(url=QDRANT_CLUSTER_URL, api_key=QDRANT_API_KEY)


def rebuild_collection():
    """Delete the collection if it exists and recreate it with the right vector size."""
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )


def ingest_document(path: str):
    """Embed each paragraph from a DOCX file and upload to Qdrant."""
    doc = Document(path)
    points = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        vector = get_embedding(text)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text, "source": os.path.basename(path)},
            )
        )
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Uploaded {len(points)} vectors from {os.path.basename(path)}")


def main():
    rebuild_collection()
    for fname in os.listdir(PAST_RFPS_DIR):
        if fname.lower().endswith(".docx"):
            ingest_document(os.path.join(PAST_RFPS_DIR, fname))
    print("Qdrant database rebuild complete.")


if __name__ == "__main__":
    main()
