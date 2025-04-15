import json
import requests
import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchParams
from dotenv import load_dotenv
load_dotenv()

# Config
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_CLUSTER_URL = "https://295f06f4-25f8-4197-bd5e-2227d256a1f1.us-east4-0.gcp.cloud.qdrant.io:6333"
COLLECTION_NAME = "past_rfp_answers"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
EXTRACTED_QUESTIONS_PATH = "output/extracted_questions.json"

# Helper - get ollama embedding


def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": OLLAMA_EMBEDDING_MODEL, "PROMPT": text}
    )
    return response.json()["embedding"]


# Load questions
with open(EXTRACTED_QUESTIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

client = QdrantClient(
    url=QDRANT_CLUSTER_URL,
    api_key=QDRANT_API_KEY
)

# Loop through all files and questions
for filename, questions in data.items():
    print(f"\n📄 Processing file: {filename}")

    for i, question in enumerate(questions, 1):
        print(f"\n🔎 Q{i}: {question}")

        vector = get_embedding(question)

        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=3,
            with_payload=True,
            search_params=SearchParams(hnsw_ef=128)
        )

        print("🧠 Top Matches:")
        for idx, match in enumerate(results, 1):
            print(f" #{idx} (score: {match.score:.4f})")
            print(f" Q: {match.payload['question']}")
            print(f" A: {match.payload['answer'][:200]}...\n")
