import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# ✅ Step 1: Load .env file
load_dotenv()

# ✅ Step 2: Retrieve API key
api_key = os.getenv("QDRANT_API_KEY")

# ✅ Step 3: Initialize client with key
client = QdrantClient(
    url="https://295f06f4-25f8-4197-bd5e-2227d256a1f1.us-east4-0.gcp.cloud.qdrant.io",
    api_key=api_key
)

# ✅ Step 4: Test it
print(client.get_collections())
