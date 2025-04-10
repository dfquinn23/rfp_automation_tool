import json
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, SearchRequest, SearchParams
from dotenv import load_dotenv
import os
load_dotenv()

# configure
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_CLUSTER_URL = "https://295f06f4-25f8-4197-bd5e-2227d256a1f1.us-east4-0.gcp.cloud.qdrant.io:6333"
COLLECTION_NAME = "past_rfp_answers"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
EXTRACTED_QUESTIONS_PATH = "output/extracted_questions.json"


# HELPER - EMBED THE NEW QUESTION
def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}
    )
    return response.json()["embedding"]


# Load the first new RFP question
with open(EXTRACTED_QUESTIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

first_doc = list(data.values())[0]
first_question = first_doc[0]
print(f"\n🔎 Searching Qdrant for question:\n➡️ {first_question}")

# Embed it
vector = get_embedding(first_question)

# Connect to Qdrant and search
client = QdrantClient(
    url=QDRANT_CLUSTER_URL,
    api_key=QDRANT_API_KEY
)

results = client.search(
    collection_name=COLLECTION_NAME,
    query_vector=vector,
    limit=5,
    with_payload=True,
    search_params=SearchParams(hnsw_ef=128)
)

# Display results
print("\n🧠 Top Matches:")
for i, res in enumerate(results, 1):
    print(f"\n#{i} (score: {res.score:.4f})")
    print("Q:", res.payload["question"])
    print("A:", res.payload["answer"])
