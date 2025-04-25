import requests


def notify_n8n(filename, client):
    try:
        url = "http://127.0.0.1:5678/webhook/new_rfp_uploaded"
        payload = {
            "filename": filename,
            "client": client
        }

        response = requests.post(url, json=payload)
        print(f"[WEBHOOK] Sent to {url}", flush=True)
        print(f"[WEBHOOK] Status: {response.status_code}", flush=True)
        print(f"[WEBHOOK] Body: {response.text}", flush=True)

        response.raise_for_status()

    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}", flush=True)
