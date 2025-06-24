# CLOUD COMPATIBLE:
# In core/generate.py

# core/generate.py (The final, complete version)

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# --- Step 1: Robustly load environment variables ---
# This ensures the script always finds the .env file, no matter how it's called.
try:
    project_root = Path(__file__).resolve().parent.parent
    dotenv_path = project_root / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path=dotenv_path)
except Exception as e:
    print(
        f"Warning: Could not load .env file. Relying on system environment variables. Error: {e}")

# --- Step 2: Initialize the OpenAI client ---
# The OpenAI library automatically finds the OPENAI_API_KEY in the loaded environment.
try:
    client = OpenAI()
    if not client.api_key:
        raise ValueError(
            "OpenAI API key not found. Please check your .env file or environment variables.")
except Exception as e:
    # If initialization fails, create a placeholder client to avoid crashing, and print an error.
    print(f"CRITICAL ERROR: Failed to initialize OpenAI client. {e}")
    client = None

# Set the model name
EMBEDDING_MODEL = "text-embedding-3-small"


# --- THIS IS THE FUNCTION THAT WAS MISSING ---
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
        # Provide a more specific error message.
        print(f"ERROR during OpenAI API call: {e}")
        raise RuntimeError(
            f"OpenAI embedding failed. Please check your API key, network connection, and account status. Error: {e}")


# --- THIS IS THE FUNCTION WE UPDATED ---
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
