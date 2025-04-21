import os
from dotenv import load_dotenv

load_dotenv()

# Model & API configuration
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_GENERATION_MODEL = "llama3"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_GENERATION_MODEL = "gpt-4-turbo"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_CLUSTER_URL = os.getenv("QDRANT_CLUSTER_URL")
COLLECTION_NAME = "past_rfp_answers"
REVIEW_SCORE_THRESHOLD = 0.60
USE_OPENAI = True

# Paths
LOG_DIR = "logs"
OUTPUT_DIR = "output"
