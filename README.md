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
