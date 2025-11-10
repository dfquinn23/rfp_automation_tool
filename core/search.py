# core/search.py
# Production-ready Qdrant search with proper error handling

import streamlit as st
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchParams
from qdrant_client.http.exceptions import UnexpectedResponse


@st.cache_resource
def get_qdrant_client():
    """
    Initialize and return a cached QdrantClient connected to the cluster.
    
    This function is cached so the connection is only made once per session,
    improving performance and reducing connection overhead.
    
    Returns:
        QdrantClient instance or None if connection fails
    """
    try:
        client = QdrantClient(
            url=st.secrets["QDRANT_CLUSTER_URL"],
            api_key=st.secrets["QDRANT_API_KEY"],
        )
        print("[INFO] Successfully connected to Qdrant.")
        return client
    except KeyError as e:
        st.error(f"Missing required secret: {e}. Please configure Streamlit secrets.")
        print(f"[ERROR] Missing Qdrant configuration: {e}")
        return None
    except Exception as e:
        st.error(f"Failed to connect to Qdrant: {e}")
        print(f"[ERROR] Qdrant connection failed: {e}")
        return None


def search_qdrant(vector, limit=5, min_score=0.3):
    """
    Perform a semantic search on the Qdrant collection.
    
    Args:
        vector: The embedding vector to search with (1536 dimensions for OpenAI)
        limit: Maximum number of results to return (default: 5)
        min_score: Minimum similarity score threshold (default: 0.3)
        
    Returns:
        List of search results (ScoredPoint objects) or empty list if error occurs
        
    Note:
        Results are automatically filtered by min_score to exclude low-quality matches
    """
    client = get_qdrant_client()
    if client is None:
        st.error("Qdrant client is not available. Cannot perform search.")
        return []
    
    # Get collection name from secrets with fallback
    collection_name = st.secrets.get("COLLECTION_NAME", "past_rfp_answers")

    try:
        results = client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
            with_payload=True,
            search_params=SearchParams(hnsw_ef=128)  # HNSW search parameter for quality
        )
        
        # Filter out low-confidence results
        filtered_results = [r for r in results if r.score >= min_score]
        
        if len(filtered_results) < len(results):
            print(f"[INFO] Filtered {len(results) - len(filtered_results)} low-score results")
        
        return filtered_results

    except UnexpectedResponse as e:
        # Collection doesn't exist
        st.error(
            f"⚠️ Collection '{collection_name}' not found in Qdrant. "
            "Please rebuild the database using the 'Database Management' section."
        )
        print(f"[ERROR] Collection '{collection_name}' not found in Qdrant.")
        return []
        
    except Exception as e:
        st.error(f"An error occurred during search: {e}")
        print(f"[ERROR] Qdrant search failed: {e}")
        return []
