# run_pipeline.py (The final, complete, and correctly structured version)

from core.logger import log_result
from core.search import search_qdrant
from core.generate import get_embedding, generate_draft_answer
from core.extract import extract_questions_from_docx
from core.config import OUTPUT_DIR, REVIEW_SCORE_THRESHOLD
import os
import argparse
from docx import Document
from docx.shared import Pt
from pathlib import Path
from dotenv import load_dotenv

# --- Load environment variables reliably ---
project_root = Path(__file__).parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

# --- Import your project's core functions ---


def run_pipeline(input_path: str):
    """
    The main pipeline function that processes an RFP document from start to finish.
    """
    print(f"\n[-->] Loading RFP: {input_path}")
    questions = extract_questions_from_docx(input_path)
    if not questions:
        print("X No valid questions found in the document.")
        return

    print(
        f"Extracted {len(questions)} questions. Starting draft generation...\n")

    # --- Initialize Word documents for output ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    full_doc = Document()
    full_doc.add_heading("RFP Draft Responses", level=1)

    review_doc = Document()
    review_doc.add_heading("[!] Needs Review", level=1)

    # --- This loop is now correctly INSIDE the function ---
    for i, question in enumerate(questions, 1):
        print(f"Processing Q{i}: {question[:100]}...")

        # Get embedding and search Qdrant
        vector = get_embedding(question)
        results = search_qdrant(vector)

        # Generate the draft answer using the search results
        draft = generate_draft_answer(question, results)

        # Determine if the draft needs human review based on the top score
        top_score = results[0].score if results else 0.0
        needs_review = top_score < REVIEW_SCORE_THRESHOLD

        if not results or needs_review:
            draft = f"[⚠ Needs review | Top Score: {top_score:.2f}]\n{draft}"

        # Log the outcome for this question
        log_result({
            "question": question,
            "top_score": top_score,
            "needs_review": needs_review,
            "draft": draft
        })

        # Add the question and generated draft to the main .docx file
        p_q = full_doc.add_paragraph()
        run_q = p_q.add_run(f"Q{i}: {question}")
        run_q.bold = True
        run_q.font.size = Pt(11)
        p_q.space_after = Pt(6)

        p_a = full_doc.add_paragraph(draft)
        p_a.space_after = Pt(14)

        # If it needs review, also add it to the separate review .docx file
        if needs_review:
            p_q_r = review_doc.add_paragraph()
            run_q_r = p_q_r.add_run(f"Q{i}: {question}")
            run_q_r.bold = True
            run_q_r.font.size = Pt(11)
            p_q_r.space_after = Pt(6)

            p_a_r = review_doc.add_paragraph(draft)
            p_a_r.space_after = Pt(14)

    # --- Save the generated Word documents ---
    full_path = os.path.join(OUTPUT_DIR, "generated_rfp_draft.docx")
    full_doc.save(full_path)
    print(f"\n✅ Full draft saved to: {full_path}")

    # Only save the review document if it contains questions
    if len(review_doc.paragraphs) > 1:
        review_path = os.path.join(OUTPUT_DIR, "low_confidence_rfp_draft.docx")
        review_doc.save(review_path)
        print(f"ℹ️ Low-confidence draft saved to: {review_path}")


# This part allows the script to be run from the command line for local testing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run full RFP automation pipeline.")
    parser.add_argument("--rfp", required=True,
                        help="Path to new RFP .docx file")
    args = parser.parse_args()
    run_pipeline(args.rfp)
