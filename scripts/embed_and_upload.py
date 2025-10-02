from pathlib import Path
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from qdrant_client import QdrantClient
import requests
import uuid
import os
import json
from dotenv import load_dotenv
load_dotenv()


# --Configuration--

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_CLUSTER_URL = "https://13234bf2-e863-42bc-b01a-76d0c453560b.eu-west-2-0.aws.cloud.qdrant.io"
COLLECTION_NAME = "past_rfp_answers"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
QA_PATH = "output/past_rfps_qa.json"

# Connect to Qdrant
client = QdrantClient(
    url=QDRANT_CLUSTER_URL,
    api_key=QDRANT_API_KEY
)

print("🔌 Connecting to Qdrant...")
print(client.get_collections())

# 🔄 Wipe and recreate the collection
if client.collection_exists(COLLECTION_NAME):
    print(f"🧨 Deleting existing collection: {COLLECTION_NAME}")
    client.delete_collection(collection_name=COLLECTION_NAME)

print(f"🛠️ Creating new collection: {COLLECTION_NAME}")
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)
print("✅ Collection created successfully.")


# Load extracted Q&A pairs
with open(QA_PATH, "r", encoding="utf-8") as f:
    qa_pairs = json.load(f)

# Helper - get embeddings from Ollama


def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}
    )
    return response.json()["embedding"]


# Upload each answer as a point
points = []
for pair in qa_pairs:
    question = pair["question"]
    answer = pair["answer"]
    if not answer.strip():
        print(f"⚠️ Skipping empty answer: {question[:60]}")
        continue

    vector = get_embedding(answer)
    if not vector:
        print(f"❌ Failed to get embedding for: {question[:60]}")
        continue

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "question": question,
            "answer": answer,
            "source": "past_rfp_qa.json"
        }
    )

    points.append(point)

    # Push to Qdrant
client.upsert(collection_name=COLLECTION_NAME, points=points)

print(
    f"✅ Uploaded {len(points)} Q&A embeddings to Qdrant collection: {COLLECTION_NAME}")
