# core/config.py
# Production-ready configuration for Streamlit Cloud deployment

import os
import streamlit as st
from dotenv import load_dotenv

# Load .env for local development (ignored in production)
load_dotenv()

# Model & API configuration - prioritize Streamlit secrets over environment variables
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"  # For local development only
OLLAMA_GENERATION_MODEL = "llama3"  # For local development only
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL_NAME = "gpt-4"
OPENAI_GENERATION_MODEL = "gpt-4-turbo"
QDRANT_API_KEY = st.secrets.get("QDRANT_API_KEY", os.getenv("QDRANT_API_KEY"))
QDRANT_CLUSTER_URL = st.secrets.get("QDRANT_CLUSTER_URL", os.getenv("QDRANT_CLUSTER_URL"))
COLLECTION_NAME = st.secrets.get("COLLECTION_NAME", "past_rfp_answers")
REVIEW_SCORE_THRESHOLD = 0.60
USE_OPENAI = True

# Paths
LOG_DIR = "logs"
OUTPUT_DIR = "output"
PAST_RFPS_DIR = "past_rfps"

# NOTE: Qdrant client is NOT initialized here to avoid conflicts.
# Always use get_qdrant_client() from core.search instead.

