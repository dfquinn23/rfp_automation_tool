from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchParams
from core.config import QDRANT_CLUSTER_URL, QDRANT_API_KEY, COLLECTION_NAME

client = QdrantClient(url=QDRANT_CLUSTER_URL, api_key=QDRANT_API_KEY)


def search_qdrant(vector, limit=3):
    return client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=limit,
        with_payload=True,
        search_params=SearchParams(hnsw_ef=128)
    )
