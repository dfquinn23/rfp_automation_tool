# core/generate.py
# CLOUD-COMPATIBLE VERSION

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# --- Step 1: Robustly load environment variables ---
try:
    project_root = Path(__file__).resolve().parent.parent
    dotenv_path = project_root / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path=dotenv_path)
except Exception as e:
    print(f"Warning: Could not load .env file. Relying on Streamlit secrets. Error: {e}")

# --- Step 2: Initialize the OpenAI client ---
# Get API key from Streamlit secrets first, then fall back to environment variables
try:
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    if not api_key:
        raise ValueError("OpenAI API key not found in secrets or environment variables.")
    
    client = OpenAI(api_key=api_key)
    print("[INFO] Successfully initialized OpenAI client.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize OpenAI client. {e}")
    client = None

# Set the model name
EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(text: str) -> list[float]:
    """
    Get embedding for a given text using OpenAI's embedding API.
    """
    if not client:
        raise RuntimeError(
            "OpenAI client is not initialized. Cannot get embeddings.")

    try:
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"ERROR during OpenAI API call: {e}")
        raise RuntimeError(
            f"OpenAI embedding failed. Please check your API key, network connection, and account status. Error: {e}")


def generate_draft_answer(question: str, retrieved_context: list) -> str:
    """
    Generate a draft RFP answer by combining the top-matched Qdrant responses.
    """
    if not retrieved_context:
        return "No relevant information found in the database."

    base_answer = ""
    for i, item in enumerate(retrieved_context):
        # Correctly look for "text_content"
        answer_piece = item.payload.get("text_content", "").strip()
        source_file = item.payload.get("source_file", "N/A")

        if answer_piece:
            # Add the source file and score for better context
            base_answer += f"[Source: {source_file} | Score: {item.score:.2f}]\n{answer_piece}\n\n"

    if not base_answer:
        return "Matches were found, but they had no text content."

    return base_answer.strip()
