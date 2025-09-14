from typing import List, Dict, Any
import logging
import weaviate

logger = logging.getLogger(__name__)

# document_retriever.py: This file contains the WeaviateRetriever class, which is responsible for retrieving relevant
# documents from the Weaviate database.

class WeaviateRetriever:
    def __init__(self, client: weaviate.Client):
        self.client = client

    def retrieve(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from Weaviate based on the given query.

        :param query: The search query
        :param top_k: Number of top results to return
        :return: List of relevant documents
        """
        try:
            result = (
                self.client.query
                .get("Document", ["content", "source"])
                .with_bm25(query=query)
                .with_limit(top_k)
                .do()
            )
            return result["data"]["Get"]["Document"]
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []