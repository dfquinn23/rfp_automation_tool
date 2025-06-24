# rebuild_qdrant_embeddings.py

import uuid
from docx import Document
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from core.embed import get_embedding
from core.config import COLLECTION_NAME
import os
import sys

# Ensure project root is in path for 'core' module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_CLUSTER_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

PAST_RFPS_DIR = "past_rfps"

# Delete the existing collection
if COLLECTION_NAME in [c.name for c in client.get_collections().collections]:
    client.delete_collection(collection_name=COLLECTION_NAME)
    print(f"🗑️ Deleted existing collection: {COLLECTION_NAME}")

# Re-create and embed all .docx files in past_rfps/
for file_name in os.listdir(PAST_RFPS_DIR):
    if file_name.endswith(".docx"):
        file_path = os.path.join(PAST_RFPS_DIR, file_name)
        print(f"📄 Embedding: {file_path}")

        doc = Document(file_path)
        points = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            vector = get_embedding(text)
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"source": file_name}
            ))

        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✅ Uploaded: {file_name}")

print("🎉 Rebuild complete.")
