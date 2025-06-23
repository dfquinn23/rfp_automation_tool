from pathlib import Path
from core.embed import embed_final_rfp, ensure_correct_collection


def main():
    """Embed all past RFPs into Qdrant."""
    ensure_correct_collection()

    rfp_dir = Path("past_rfps")
    doc_paths = sorted(rfp_dir.glob("*.docx"))

    if not doc_paths:
        print("No .docx files found in 'past_rfps/'.")
        return

    total = 0
    for doc_path in doc_paths:
        print(f"Embedding {doc_path.name}...")
        embed_final_rfp(str(doc_path))
        total += 1

    print(f"Processed {total} document{'s' if total != 1 else ''}.")


if __name__ == "__main__":
    main()
