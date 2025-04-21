# This is a command-line testing tool that makes it easy to:
# Run one question at a time
# See the top 3 matched answers (with similarity scores)
# View the generated draft
# Spot [⚠ Needs review] tagging
# Use it for debugging, refining, or demo purposes

import argparse
from qa_generation import generate_reviewable_draft


def run_test(question):
    result = generate_reviewable_draft(question)

    print("\n 🔎 New Question:")
    print(f"➡️{result['question']}")

    print("\n📊 Top Qdrant Matches:")
    for i, answer in enumerate(result['top_answers'], 1):
        print("\n#{i} (match score ~ {resulty['top score']:.4f}):\n{answer}")

    print("\n📝 Generated Draft Answer:")
    print(result["draft"])

    if result["needs_review"]:
        print("\n⚠️ This answer needs review(low similarity score).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test a single RFP question with draft generation.")
    parser.add_argument("question", type=str,
                        help="The RFP question to test (enclose in quotes)")

    args = parser.parse_args()
    run_test(args.question)
