import argparse
import json
import os
from datetime import datetime
from qa_generation import generate_reviewable_draft

LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "draft_log.jsonl")


def run_test(question):
    result = generate_reviewable_draft(question)

    # Print to terminal
    print("\n🔎 New Question:")
    print(f"➡️ {result['question']}")
    print("\n📊 Top Qdrant Matches:")
    for i, answer in enumerate(result['top_answers'], 1):
        print(f"\n#{i} (score: {result['top_score']:.4f})\n{answer}")
    print("\n📝 Generated Draft Answer:\n" + result['draft'])

    if result["needs_review"]:
        print("\n⚠️ This answer needs review (low similarity score).")

    # Save to log
    os.makedirs(LOG_DIR, exist_ok=True)
    result_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": result["question"],
        "top_score": result["top_score"],
        "needs_review": result["needs_review"],
        "top_answers": result["top_answers"],
        "draft": result["draft"]
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(result_entry, ensure_ascii=False) + "\n")

    print(f"\n📝 Result saved to: {LOG_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test and log a single RFP question.")
    parser.add_argument("question", type=str,
                        help="The RFP question to test (use quotes)")

    args = parser.parse_args()
    run_test(args.question)
