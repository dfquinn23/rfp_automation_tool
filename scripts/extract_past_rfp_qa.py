# C:/Users/Daniel Quinn/Desktop/AI_Consultancy_Project/rfp_assistant/rfp_automation_tool/new_rfps/new_incoming_sample_rfp_1.docx"

from docx import Document
import os
import json


def extract_qa_pairs(file_path):
    doc = Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    qa_pairs = []
    i = 0
    while i < len(paragraphs):
        if paragraphs[i].endswith("?"):
            question = paragraphs[i]
            answer = paragraphs[i+1] if i + 1 < len(paragraphs) else ""
            qa_pairs.append({
                "question": question,
                "answer": answer
            })
            i += 2
        else:
            i += 1
    return qa_pairs


if __name__ == "__main__":
    file_path = "C:/Users/Daniel Quinn/Desktop/AI_Consultancy_Project/rfp_assistant/rfp_automation_tool/new_rfps/new_incoming_sample_rfp_1.docx"
    if not os.path.exists(file_path):
        print(f"File not found {file_path}")
        exit()

    qa_pairs = extract_qa_pairs(file_path)

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "past_rfps_qa.json")

    with open(output_path, "w",  encoding="utf-8") as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted {len(qa_pairs)} Q&A pairs")
    print(f"📝 Saved to: {output_path}")
