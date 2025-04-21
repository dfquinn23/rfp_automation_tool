import requests
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchParams
from generate_drafts import generate_draft_answer
import os
from dotenv import load_dotenv

load_dotenv()

# Config
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_CLUSTER_URL = "https://295f06f4-25f8-4197-bd5e-2227d256a1f1.us-east4-0.gcp.cloud.qdrant.io:6333"
COLLECTION_NAME = "past_rfp_answers"
EMBED_MODEL = "nomic-embed-text"
GEN_MODEL = "llama3"
REVIEW_THRESHOLD = 0.60

# connect to Qdrant
client = QdrantClient(
    url=QDRANT_CLUSTER_URL,
    api_key=QDRANT_API_KEY

)

# Core Helper


def generate_reviewable_draft(question):
    # 1 Embed Questions
    embed_resp = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": question}
    )
    embedding = embed_resp.json()["embedding"]

    # 2. Query Qdrant
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=3,
        with_payload=True,
        search_params=SearchParams(hnsw_ef=128)

    )

    top_answers = [r.payload["answer"] for r in results]
    top_score = results[0].score if results else 0.0
    needs_review = top_score < REVIEW_THRESHOLD

    # 3 Draft
    instruction = (
        "Use the first example answer as a foundation. Improve or expand it using insight from the others, "
        "and generate a concise, professional response. "
        "Only use information found in the provided answers. Do not make assumptions or fabricate facts."
    )

    draft = generate_draft_answer(
        question,
        top_answers,
        model=GEN_MODEL,
        extra_instruction=instruction
    )

    if needs_review:
        draft = f"[⚠ Needs review: low similarity score ({top_score:.2f})]\n\n{draft}"

    return {
        "question": question,
        "top_answers": top_answers,
        "draft": draft,
        "needs_review": needs_review,
        "top_score": top_score
    }
