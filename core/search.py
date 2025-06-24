# search.py
# core/search.py

import streamlit as st
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

# --- New, Recommended Initialization ---
# This function initializes the Qdrant client using Streamlit's secrets.
# @st.cache_resource ensures this expensive connection is only made once.


@st.cache_resource
def get_qdrant_client():
    """Initializes and returns a QdrantClient connected to the cluster specified in Streamlit secrets."""
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


# Get the client instance.
client = get_qdrant_client()
COLLECTION_NAME = st.secrets["COLLECTION_NAME"]


# --- Your Search Function (Slightly Modified) ---
def search_qdrant(vector, limit=5, min_score=0.3):
    """Performs a search on the Qdrant collection."""
    if client is None:
        st.error("Qdrant client is not available. Cannot perform search.")
        return []

    try:
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=limit,
            with_payload=True,
            search_params=SearchParams(hnsw_ef=128)
        )
        # Optional: filter low-score results
        return [r for r in results if r.score >= min_score]

    except UnexpectedResponse as e:
        # This is the specific error you were getting!
        # It means the connection worked but the collection wasn't found.
        st.error(
            f"Collection '{COLLECTION_NAME}' not found in Qdrant. Please run the one-time database setup script.")
        print(
            f"[ERROR] Collection '{COLLECTION_NAME}' not found. Did you run the setup script?")
        return []
    except Exception as e:
        st.error(f"An error occurred during Qdrant search: {e}")
        print(f"[ERROR] An error occurred during Qdrant search: {e}")
        return []
