# core/generate.py
import os
import openai
import requests
import json
from openai import OpenAI
from core.config import (
    OLLAMA_GENERATION_MODEL,
    OPENAI_API_KEY,
    OPENAI_GENERATION_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    USE_OPENAI
)

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str, use_openai: bool = USE_OPENAI) -> list:
    if use_openai:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            # or you can dynamically pull from OPENAI_MODEL_NAME if you want
            model="text-embedding-ada-002",
            input=text,
        )
        return response.data[0].embedding
    else:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}
        )
        return response.json()["embedding"]


try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("[DEBUG] Connected to OpenAI")
except Exception as e:
    print(f"[ERROR] OpenAI connection failed: {e}")
    raise


def generate_draft_answer_openai(question, top_answers, model=OPENAI_GENERATION_MODEL):
    messages = [
        {"role": "system", "content": "You are a professional RFP assistant for an investment firm."},
        {"role": "user",
            "content": f"""Use the first example answer as a base. Improve it with insights from the others.\n\nQuestion: {question}\n\nExample answers:\n{chr(10).join(top_answers)}\n\nRespond professionally, accurately, and concisely."""}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def generate_draft_answer_ollama(question, top_answers, model=OLLAMA_GENERATION_MODEL, extra_instruction=None):
    examples = "\n\n".join(top_answers)
    base_prompt = f"Question: {question}\n\nExamples:\n{examples}"

    if extra_instruction:
        prompt = f"{extra_instruction}\n\n{base_prompt}"
    else:
        prompt = base_prompt

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt},
        stream=True
    )

    chunks = []
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            chunks.append(data.get("response", ""))

    return "".join(chunks).strip()


def generate_draft_answer(question, top_answers):
    if USE_OPENAI:
        return generate_draft_answer_openai(question, top_answers)
    else:
        return generate_draft_answer_ollama(question, top_answers)
