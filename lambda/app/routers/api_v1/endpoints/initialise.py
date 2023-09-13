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
from langchain.llm.sagemaker_endpoint import LLMContentHandler
import time

logger = logging.getLogger(__name__)

#  fetch value from aws parameter store

ssm = boto3.client('ssm')
region = ssm.get_parameter(Name='REGION', WithDecryption=True)['Parameter']['Value']


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

# class for serializing/deserializing requests/responses to/from the embeddings model
class ContentHandlerForEmbeddings(EmbeddingsContentHandler):
    """
    encode input string as utf-8 bytes, read the embeddings
    from the output
    """
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs={}) -> bytes:
        input_str = json.dumps({"text_input": prompt, **model_kwargs})
        return input_str.encode('utf-8')
    
    def transform_output(self, output: bytes) -> List[str]:
        response_json = json.loads(output.read().decode("utf-8"))
        embeddings = response_json["embedding"]
        if len(embeddings) == 1:
            return [embeddings[0]]
        return embeddings

# class for serializing/deserializing requests/responses to/from the llm model
class ContentHandlerForTextGeneration(LLMContentHandler):
    """
    encode input string as utf-8 bytes, read the text generation 
    from the output
    """
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs={}) -> bytes:
        input_str = json.dumps({"text_input": prompt, **model_kwargs})
        return input_str.encode('utf-8')
    
    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["generated_texts"][0]


# create the embedding
def _create_sagemaker_embeddings(endpoint_name: str, region: str) -> SagemakerEndpointEmbeddingsJumpStart:
    """
    Args:
        endpoint_name: The name of the Sagemaker Inference Endpoint.
        region: The region of the Sagemaker Inference Endpoint.
    """

    # create a content handler object which knows how to serialize
    # and deserialize communication with the model endpoint

    content_handler_for_embeddings = ContentHandlerForEmbeddings()

    # Sagemakder endpoint that will be used to embed query

    embeddings = SagemakerEndpointEmbeddingsJumpStart(
        endpoint_name=endpoint_name,
        region_name=region,
        content_handler=content_handler_for_embeddings
    )
    logger.info(f"embeddings type={type(embeddings)}")
    return embeddings
