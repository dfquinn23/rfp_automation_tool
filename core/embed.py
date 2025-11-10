# core/embed.py
# Production-ready embedding with proper Q&A extraction

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
    Recreate the Qdrant collection with correct vector dimensions and distance metric.
    
    WARNING: This deletes all existing data in the collection.
    Only call this when explicitly setting up or resetting the database.
    """
    client = get_qdrant_client()
    if client is None:
        raise RuntimeError("Qdrant client is not available.")
    
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,  # Required by OpenAI text-embedding-3-small
                distance=Distance.COSINE
            )
        )
        print(f"[INFO] Collection '{COLLECTION_NAME}' recreated with 1536 dimensions.")
    except Exception as e:
        print(f"[ERROR] Could not recreate collection: {e}")
        raise


def extract_qa_from_docx(file_path):
    """
    Extract question-answer pairs from a DOCX file.
    
    Format assumption: Questions end with '?' and are immediately followed by 
    their answer in the next paragraph.
    
    Args:
        file_path: Path to the .docx file
        
    Returns:
        List of dicts with 'question' and 'answer' keys
    """
    doc = Document(file_path)
    qa_pairs = []
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    i = 0
    while i < len(paras):
        if paras[i].endswith("?"):
            question = paras[i]
            answer = paras[i + 1] if i + 1 < len(paras) else ""
            
            # Only add pairs that have both question and answer
            if answer and not answer.endswith("?"):  # Answer shouldn't be another question
                qa_pairs.append({
                    "question": question,
                    "answer": answer
                })
                i += 2  # Skip both question and answer
            else:
                print(f"[WARNING] Question without valid answer: {question[:60]}...")
                i += 1
        else:
            i += 1
    
    return qa_pairs


def embed_final_rfp(file_path):
    """
    Load a final RFP draft from DOCX, extract Q&A pairs, and upload to Qdrant.
    
    IMPORTANT: Only the ANSWERS are embedded, not the questions. This prevents
    questions from polluting search results. The questions are stored in the
    payload for reference.
    
    Args:
        file_path: Path to the finalized RFP .docx file
        
    Raises:
        RuntimeError: If Qdrant client is unavailable
    """
    client = get_qdrant_client()
    if client is None:
        raise RuntimeError("Qdrant client is not available. Cannot embed RFP.")

    # Extract Q&A pairs from the document
    qa_pairs = extract_qa_from_docx(file_path)
    
    if not qa_pairs:
        print(f"[WARNING] No Q&A pairs found in {file_path}. Check document format.")
        return
    
    print(f"[INFO] Extracted {len(qa_pairs)} Q&A pairs from {os.path.basename(file_path)}")
    
    points = []
    skipped = 0
    
    for pair in qa_pairs:
        answer = pair["answer"].strip()
        question = pair["question"].strip()
        
        if not answer or len(answer) < 10:
            print(f"[WARNING] Skipping too-short answer for: {question[:60]}...")
            skipped += 1
            continue

        try:
            # Embed ONLY the answer (not the question)
            vector = get_embedding(answer)
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                payload={
                    "question": question,      # Store for reference
                    "answer": answer,          # This is what we embedded
                    "source": os.path.basename(file_path)
                },
                vector=vector
            )
            points.append(point)
            
        except Exception as e:
            print(f"[ERROR] Failed to embed answer for '{question[:60]}...': {e}")
            skipped += 1

    if points:
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"[INFO] Successfully uploaded {len(points)} Q&A pairs to Qdrant.")
            if skipped > 0:
                print(f"[INFO] Skipped {skipped} invalid entries.")
        except Exception as e:
            print(f"[ERROR] Failed to upload to Qdrant: {e}")
            raise
    else:
        print(f"[WARNING] No valid points to upload from {file_path}")
