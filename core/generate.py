# CLOUD COMPATIBLE:
# core/generate.py

import os
import streamlit as st
from openai import OpenAI
from qdrant_client.http.models import ScoredPoint  # if needed for type hint


# Load from Streamlit secrets or fallback to env for local dev
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Set the model name
EMBEDDING_MODEL = "text-embedding-3-small"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list:
    """
    Get embedding for a given text using OpenAI's embedding API.
    """
    try:
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"OpenAI embedding failed: {e}")


def generate_draft_answer(question: str, retrieved_context: list) -> str:
    """
    Generate a draft RFP answer by combining the top-matched Qdrant responses.

    Args:
        question: The RFP question.
        retrieved_context: List of Qdrant search results (with `.payload["answer"]`).

    Returns:
        Draft answer as a string.
    """
    base_answer = ""
    for i, item in enumerate(retrieved_context):
        answer_piece = item.payload.get("answer", "").strip()
        if answer_piece:
            base_answer += f"[Source {i+1}] {answer_piece}\n\n"

    if not base_answer:
        return "[⚠ Needs review] No confident matches found."

    return base_answer.strip()


# LOCAL ONLY
# core/generate.py
# import os
# import openai
# import requests
# import json
# from openai import OpenAI
# from core.config import (
#     OLLAMA_GENERATION_MODEL,
#     OPENAI_API_KEY,
#     OPENAI_GENERATION_MODEL,
#     OLLAMA_EMBEDDING_MODEL,
#     USE_OPENAI
# )

# client = OpenAI(api_key=OPENAI_API_KEY)


# def get_embedding(text: str, use_openai: bool = USE_OPENAI) -> list:
#     if use_openai:
#         client = openai.OpenAI(api_key=OPENAI_API_KEY)
#         response = client.embeddings.create(
#             # or you can dynamically pull from OPENAI_MODEL_NAME if you want
#             model="text-embedding-ada-002",
#             input=text,
#         )
#         return response.data[0].embedding
#     else:
#         response = requests.post(
#             "http://localhost:11434/api/embeddings",
#             json={"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}
#         )
#         return response.json()["embedding"]


# try:
#     client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     print("[DEBUG] Connected to OpenAI")
# except Exception as e:
#     print(f"[ERROR] OpenAI connection failed: {e}")
#     raise


# def generate_draft_answer_openai(question, top_answers, model=OPENAI_GENERATION_MODEL):
#     messages = [
#         {"role": "system", "content": "You are a professional RFP assistant for an investment firm."},
#         {"role": "user",
#             "content": f"""Use the first example answer as a base. Improve it with insights from the others.\n\nQuestion: {question}\n\nExample answers:\n{chr(10).join(top_answers)}\n\nRespond professionally, accurately, and concisely."""}
#     ]

#     response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=0.3
#     )
#     return response.choices[0].message.content.strip()


# def generate_draft_answer_ollama(question, top_answers, model=OLLAMA_GENERATION_MODEL, extra_instruction=None):
#     examples = "\n\n".join(top_answers)
#     base_prompt = f"Question: {question}\n\nExamples:\n{examples}"

#     if extra_instruction:
#         prompt = f"{extra_instruction}\n\n{base_prompt}"
#     else:
#         prompt = base_prompt

#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": model, "prompt": prompt},
#         stream=True
#     )

#     chunks = []
#     for line in response.iter_lines():
#         if line:
#             data = json.loads(line)
#             chunks.append(data.get("response", ""))

#     return "".join(chunks).strip()


# def generate_draft_answer(question, top_answers):
#     if USE_OPENAI:
#         return generate_draft_answer_openai(question, top_answers)
#     else:
#         return generate_draft_answer_ollama(question, top_answers)
