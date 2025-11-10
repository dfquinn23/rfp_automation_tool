# core/embed.py
# CLOUD-COMPATIBLE VERSION - Uses consistent payload structure

import os
import uuid
from docx import Document
from qdrant_client.models import PointStruct, VectorParams, Distance
from core.generate import get_embedding
from core.search import get_qdrant_client
import streamlit as st

# Get collection name from secrets/config
COLLECTION_NAME = st.secrets.get("COLLECTION_NAME", "past_rfp_answers")


def ensure_correct_collection():
    """
    Recreate collection to ensure correct vector size and distance.
    Only call this when explicitly setting up the database.
    """
    client = get_qdrant_client()
    if client is None:
        raise RuntimeError("Qdrant client is not available.")
    
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,  # required by text-embedding-3-small
                distance=Distance.COSINE
            )
        )
        print(f"[INFO] Collection '{COLLECTION_NAME}' recreated with dim=1536.")
    except Exception as e:
        print(f"[WARNING] Could not recreate collection: {e}")


def embed_final_rfp(file_path):
    """
    Load a final RFP draft from DOCX, create embeddings for each paragraph, 
    and upload to Qdrant using the SAME payload structure as the original database.
    
    Payload structure matches original: {"answer": "...", "source": "..."}
    """
    client = get_qdrant_client()
    if client is None:
        raise RuntimeError("Qdrant client is not available. Cannot embed RFP.")

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
                payload={
                    "answer": text,  # Use "answer" to match original database structure
                    "source": os.path.basename(file_path)  # Use "source" to match original
                },
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
    else:
        print("[WARNING] No points to upload.")
