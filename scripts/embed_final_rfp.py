# Embed a final .docx file to Qdrant automatically.

import os
import json
import uuid
from dotenv import load_dotenv
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
import requests
from core.config import QDRANT_API_KEY, QDRANT_CLUSTER_URL, COLLECTION_NAME, OLLAMA_EMBEDDING_MODEL

load_dotenv()


def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}
    )
    return response.json()["embedding"]


def extract_qa_from_docx(file_path):
    doc = Document(file_path)
    qa_pairs = []
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    i = 0
    while i < len(paras):
        if paras[i].endswith("?"):
            question = paras[i]
            answer = paras[i+1] if i + 1 < len(paras) else ""
            qa_pairs.append({"question": question, "answer": answer})
            i += 2
        else:
            i += 1

    return qa_pairs


def embed_and_upload_final(file_path):
    client = QdrantClient(url=QDRANT_CLUSTER_URL, api_key=QDRANT_API_KEY)
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    qa_pairs = extract_qa_from_docx(file_path)
    points = []
    for pair in qa_pairs:
        vector = get_embedding(pair["answer"])
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "question": pair["question"],
                "answer": pair["answer"],
                "source": os.path.basename(file_path)
            }
        )
        points.append(point)

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {len(points)} final QA pairs from {file_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python embed_final_rfp.py <final_doc_path>")
        sys.exit(1)
    embed_and_upload_final(sys.argv[1])
