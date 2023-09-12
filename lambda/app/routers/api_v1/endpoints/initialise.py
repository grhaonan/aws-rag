import os
import json
import boto3
import logging
from typing import List, Callable
from urllib.parse import urlparse
from langchain.vectorstore import OpenSearchVectorStore
from langchain.vectorstore import SageMakerEndpointEmbeddings 
from .fastapi_request import Request, sagemaker_endpoint_mapping
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
import time

logger = logging.getLogger(__name__)
class SagemakerEndpointEmbeddingsJumpStart(SageMakerEndpointEmbeddings):
    def embed_documents(
            self, texts: List[str], 
            chunk_size: int = 5
    ) -> List[List[float]]:
        """Compute doc embeddings using a SageMaker Inference Endpoint.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size defines how many input texts will
                be grouped together as request. If None, will use the
                chunk size specified by the class.

        Returns:
            List of embeddings, one for each text.
        """
        results = []
        _chunk_size = len(texts) if chunk_size > len(texts) else chunk_size
        st = time.time()
        for i in range(0, len(texts), _chunk_size):
            response = self._embedding_func(texts[i:i + _chunk_size])
            results.extend(response)
        time_taken = time.time() - st
        logger.info(f"Embedding completes and it took {time_taken} seconds")
        return results
