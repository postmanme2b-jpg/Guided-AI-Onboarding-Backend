import openai
from qdrant_client import QdrantClient
from typing import Optional
import os

from config.config import (
    QDRANT_ENDPOINT,
    QDRANT_COLLECTION_NAME,
    RAG_EMBEDDING_MODEL,
    RAG_NUM_RETRIEVED_CHALLENGES
)

# === Setup clients ===

class RAGHelper:
    """
    RAG (Retrieval-Augmented Generation) helper for searching and retrieving
    challenge templates from Qdrant using OpenAI embeddings.
    
    This module provides functionality to:
    1. Get embeddings for text using OpenAI API
    2. Search Qdrant for similar challenges based on user queries
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, qdrant_api_key: Optional[str] = None):
        openai.api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.qdrant = QdrantClient(
            url=QDRANT_ENDPOINT,
            api_key=qdrant_api_key or os.environ.get("QDRANT_API_KEY"),
        )

    # === Function to get embedding from OpenAI ===
    def _get_openai_embedding(self, text: str):
        response = openai.embeddings.create(
            model=RAG_EMBEDDING_MODEL,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

    # === Search Qdrant for similar content ===
    def search_similar_challenges(self, query_text: str) -> str:
        vector = self._get_openai_embedding(query_text)

        results = self.qdrant.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=vector,
            with_payload=True,
            limit=RAG_NUM_RETRIEVED_CHALLENGES,
        )

        for hit in results.points:
            print(f"Fetched challenge: ID: {hit.payload.get('id', 'No id found')} - {hit.payload.get('name', 'No name provided')}. Score: {hit.score:.4f}")
        
        return [hit.payload for hit in results.points] if results.points else "No similar challenges found."