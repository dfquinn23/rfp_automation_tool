import os
import json
from datetime import datetime
from core.config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "draft_log.jsonl")


def log_result(entry):
    entry["timestamp"] = datetime.now().isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
