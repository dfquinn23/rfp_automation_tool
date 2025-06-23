# rfp_automation_tool
RFP Tool Prototype



rfp_automation_tool/
├── app/                     ← (streamlit app will live here)
├── core/                    ← core reusable logic
│   ├── __init__.py
│   ├── extract.py           ← question extraction
│   ├── embed.py             ← embedding via Ollama
│   ├── search.py            ← Qdrant search
│   ├── generate.py          ← llama3 draft generation
│   ├── logger.py            ← JSONL logging
│   └── config.py            ← model names, thresholds, file paths
├── scripts/                 ← command-line tools
│   ├── run_pipeline.py
│   ├── test_single_question_with_log.py
│   └── export_low_confidence_docx.py
├── output/                  ← generated docx files
├── logs/                    ← JSONL logs for audit/review
└── requirements.txt

# RFP Automation Tool

## 📄 Overview

The RFP Automation Tool streamlines the process of responding to RFPs by combining AI-based draft generation, human review, and final archiving.  
It features an intuitive Streamlit interface, low-code automation via n8n, and secure vector storage using Qdrant.

This tool is designed to help investment management firms and service providers reduce time, errors, and repetitive effort when completing new RFPs.

---

## 🚀 Features

- Upload a new RFP (.docx format)
- Auto-generate draft responses using LLM models
- Download full and low-confidence draft versions for review
- Upload final reviewed RFPs
- Archive and vectorize final RFPs for future searchability (Qdrant)
- Browse and download archived past RFPs
- Clean, client-ready Streamlit interface

---

## 🛠️ Technology Stack

- **Python** (core application)
- **Streamlit** (user interface)
- **n8n** (workflow automation)
- **Qdrant** (vector database for RFP storage and retrieval)
- **Docx** (Word document handling)
- **OpenAI API / Ollama** (for AI text generation) [adjust depending on your LLM setup]

---

## 📂 Project Structure

```plaintext
rfp_automation_tool/
│
├── core/            # Core logic (embedding, generation, config)
├── new_rfps/        # Temporary uploads of new RFPs
├── output/          # Generated drafts and low-confidence drafts
├── past_rfps/       # Finalized, archived RFPs
├── scripts/         # Optional scripts (if any)
├── run_pipeline.py  # Main pipeline controller
├── ui_streamlit.py  # Streamlit application
├── .env             # API keys and environment configs (not public)
└── README.md        # Project documentation (this file)

## 🔑 Configuration

Create a `.streamlit/secrets.toml` file and provide your API keys:

```toml
OPENAI_API_KEY = "your-openai-key"
QDRANT_API_KEY = "your-qdrant-key"
QDRANT_CLUSTER_URL = "https://<cluster-id>.cloud.qdrant.io"
```

Streamlit loads these secrets automatically when running the app or any
script that imports `streamlit`.

## ▶️ Running the App

Install the requirements and launch Streamlit:

```bash
pip install -r requirements.txt
streamlit run ui_streamlit.py
```

## 🛠 Rebuilding the Qdrant Database

Use the helper script to wipe and rebuild the vector collection from all
documents in `past_rfps/`:

```bash
python scripts/rebuild_qdrant_db.py
```

This removes any existing vectors and re-embeds each paragraph from the
archived RFPs.

