from docx import Document
import os
import sys
import json


def extract_questions_from_docx(folder_path):
    doc = Document(folder_path)
    questions = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text.endswith("?") and len(text.split()) > 3:
            questions.append(text)

    return questions

# Below is the looped code for extracting questions from a group of docs
# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python extract_questions.py <path_to_doc>")
#         sys.exit(1)

#     folder_path = sys.argv[1]

#     if not os.path.exists(folder_path):
#         print("File not found: {folder_path}")
#         sys.exit(1)

#     extracted_data = {}

#     for filename in os.listdir(folder_path):
#         if filename.endswith(".docx"):
#             file_path = os.path.join(folder_path, filename)
#             questions = extract_questions_from_docx(file_path)
#             if questions:
#                 extracted_data[filename] = questions
#                 print(f"\n✅ {filename}: {len(questions)} questions extracted")
#             else:
#                 print(f"\n⚠️ {filename}: No questions found")

#     output_path = os.path.join("output", "extracted_questions.json")
#     os.makedirs("output", exist_ok=True)

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(extracted_data, f, indent=2, ensure_ascii=False)

#     print(f"\n📝 All questions saved to: {output_path}")


# single document extraction:
if __name__ == "__main__":
    file_path = "C:/Users/Daniel Quinn/Desktop/AI Consultancy Project/rfp_assistant/new_rfps/new_incoming_sample_rfp_1.docx"

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    questions = extract_questions_from_docx(file_path)

    # save output
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "extracted_questions.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({os.path.basename(file_path): questions}, f, indent=2)

    print(f"✅ Extracted {len(questions)} questions")
    print(f"📝 Saved to{output_path} ")
