import requests
import json  # <- This is what VSCode said was missing


def generate_draft_answer(question, top_answers, model="llama3", extra_instruction=""):
    # Format the top answers
    formatted_answers = "\n".join(
        [f"{i+1}. {a.strip()}" for i, a in enumerate(top_answers)]
    )
    # Default or custom instruction
    instruction = extra_instruction.strip() if extra_instruction else (
        "Based on these examples, generate a concise and professional draft answer for the new question."
    )
    # Build the prompt
    prompt = f"""
You are helping complete a professional due diligence questionnaire.

New Question:
"{question}"

Here are similar answers we've provided in the past:
{formatted_answers}

{instruction}
""".strip()

    # Make the request to Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt},
        stream=True
    )

    response.raise_for_status()

    # Read the streamed response
    chunks = []
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            chunks.append(data.get("response", ""))

    return "".join(chunks).strip()
