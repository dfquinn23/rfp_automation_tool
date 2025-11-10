# core/generate.py
# Production-ready generation with OpenAI embeddings and question filtering

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables for local development
try:
    project_root = Path(__file__).resolve().parent.parent
    dotenv_path = project_root / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path=dotenv_path)
except Exception as e:
    print(f"[INFO] Could not load .env file. Using Streamlit secrets. {e}")

# Initialize OpenAI client with proper API key handling
try:
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    if not api_key:
        raise ValueError("OpenAI API key not found in secrets or environment variables.")
    
    client = OpenAI(api_key=api_key)
    print("[INFO] Successfully initialized OpenAI client.")
except Exception as e:
    print(f"[ERROR] Failed to initialize OpenAI client: {e}")
    client = None

EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(text: str) -> list[float]:
    """
    Get embedding for a given text using OpenAI's embedding API.
    
    Args:
        text: The text to embed
        
    Returns:
        List of floats representing the embedding vector (1536 dimensions)
        
    Raises:
        RuntimeError: If OpenAI client is not initialized or API call fails
    """
    if not client:
        raise RuntimeError("OpenAI client is not initialized. Check your API key configuration.")

    try:
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[ERROR] OpenAI API call failed: {e}")
        raise RuntimeError(f"Failed to generate embedding. Error: {e}")


def generate_draft_answer(question: str, retrieved_context: list) -> str:
    """
    Generate a draft RFP answer by combining the top-matched Qdrant responses.
    
    Features:
    - Handles multiple payload formats for backward compatibility
    - Filters out question-like results to return only actual answers
    - Includes source attribution and confidence scores
    
    Args:
        question: The RFP question being answered
        retrieved_context: List of search results from Qdrant
        
    Returns:
        String containing the formatted draft answer with sources
    """
    if not retrieved_context:
        return "No relevant information found in the database."

    base_answer = ""
    filtered_count = 0
    
    for i, item in enumerate(retrieved_context):
        # Handle multiple payload formats for backward compatibility
        answer_piece = (
            item.payload.get("answer") or         # Format 1: Original database
            item.payload.get("text") or           # Format 2: Old embed.py
            item.payload.get("text_content") or   # Format 3: Attempted fix
            ""
        ).strip()
        
        # Get source information
        source_file = (
            item.payload.get("source") or         # Format 1 & 2
            item.payload.get("source_file") or    # Format 3
            "Unknown"
        )

        if answer_piece:
            # Filter out results that are questions, not answers
            is_question = (
                answer_piece.endswith("?") or                           # Ends with question mark
                answer_piece.startswith((
                    "Q", "E.", "Please provide", "Please describe", 
                    "Please outline", "Please explain", "Complete the table", 
                    "What ", "How ", "Why ", "When ", "Where ", "Who ",
                    "Does ", "Do ", "Can ", "Could ", "Would ", "Should ",
                    "Is ", "Are ", "Have ", "Has "
                )) or
                len(answer_piece) < 20 or                               # Too short to be meaningful
                answer_piece.count("?") > 2                             # Multiple questions
            )
            
            if not is_question:
                # This looks like a real answer, include it
                base_answer += f"[Source: {source_file} | Score: {item.score:.2f}]\n{answer_piece}\n\n"
            else:
                filtered_count += 1
                print(f"[DEBUG] Filtered question-like result: {answer_piece[:80]}...")
        else:
            # Debug logging for empty results
            print(f"[DEBUG] Empty result at index {i}. Payload keys: {list(item.payload.keys())}")

    if not base_answer:
        if filtered_count > 0:
            return f"No relevant answers found. ({filtered_count} question(s) were filtered out)"
        return "Matches were found, but they contained no usable content."

    return base_answer.strip()
