# scripts/test_n8n_webhook.py
import requests

response = requests.post("http://localhost:5678/webhook/new_rfp_uploaded", json={
    "filename": "pipeline_test_2.docx",
    "client": "Client XYZ"
})

print("✅ Sent webhook:", response.status_code)
