# core/search.py
# CLOUD-COMPATIBLE VERSION

import streamlit as st
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchParams
from qdrant_client.http.exceptions import UnexpectedResponse


@st.cache_resource
def get_qdrant_client():
    """
    Initializes and returns a QdrantClient connected to the cluster specified in Streamlit secrets.
    This function is cached so the connection is only made once per session.
    """
    try:
        client = QdrantClient(
            url=st.secrets["QDRANT_CLUSTER_URL"],
            api_key=st.secrets["QDRANT_API_KEY"],
        )
        print("[INFO] Successfully connected to Qdrant.")
        return client
    except Exception as e:
        st.error(f"Failed to connect to Qdrant: {e}")
        print(f"[ERROR] Failed to connect to Qdrant: {e}")
        return None


def search_qdrant(vector, limit=5, min_score=0.3):
    """
    Performs a search on the Qdrant collection.
    
    Args:
        vector: The embedding vector to search with
        limit: Maximum number of results to return
        min_score: Minimum similarity score threshold
        
    Returns:
        List of search results, or empty list if error occurs
    """
    client = get_qdrant_client()
    if client is None:
        st.error("Qdrant client is not available. Cannot perform search.")
        return []
    
    # Get collection name from secrets, with fallback
    collection_name = st.secrets.get("COLLECTION_NAME", "past_rfp_answers")

    try:
        results = client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
            with_payload=True,
            search_params=SearchParams(hnsw_ef=128)
        )
        # Filter low-score results
        return [r for r in results if r.score >= min_score]

    except UnexpectedResponse as e:
        st.error(
            f"Collection '{collection_name}' not found in Qdrant. Please run the database setup script or check your collection name in secrets.")
        print(f"[ERROR] Collection '{collection_name}' not found. Did you run the setup script?")
        return []
    except Exception as e:
        st.error(f"An error occurred during Qdrant search: {e}")
        print(f"[ERROR] An error occurred during Qdrant search: {e}")
        return []
