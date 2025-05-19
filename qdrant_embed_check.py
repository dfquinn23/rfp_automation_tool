from qdrant_client import QdrantClient

client = QdrantClient(url="https://295f06f4-25f8-4197-bd5e-2227d256a1f1.us-east4-0.gcp.cloud.qdrant.io",
                      api_key="eREMOVED")
print(client.get_collections())
