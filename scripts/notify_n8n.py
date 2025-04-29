# scripts/notify_n8n.py
import requests


def notify_n8n(filename: str, client: str, event: str = "new_rfp_uploaded"):
    """
    Notify n8n that a new RFP draft or final draft has been uploaded.

    Args:
        filename (str): The filename of the RFP.
        client (str): Name of the client.
        event (str): Either 'new_rfp_uploaded' or 'final_draft_uploaded'
    """
    n8n_base_url = "http://localhost:5678/webhook"

    if event == "new_rfp_uploaded":
        webhook_url = f"{n8n_base_url}/new_rfp_uploaded"
    elif event == "final_draft_uploaded":
        webhook_url = f"{n8n_base_url}/final_draft_uploaded"
    else:
        raise ValueError(f"Unknown event type: {event}")

    payload = {
        "filename": filename,
        "client": client
    }

    try:
        response = requests.post(webhook_url, json=payload)
        print(f"[WEBHOOK] Sent to {webhook_url}")
        print(f"[WEBHOOK] Status: {response.status_code}")
        print(f"[WEBHOOK] Body: {response.text}")
    except Exception as e:
        print(f"[WEBHOOK] Failed to notify n8n: {e}")
