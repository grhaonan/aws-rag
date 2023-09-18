import time
import json
import logging
from typing import List
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler


logger = logging.getLogger(__name__)

# extend the SagemakerEndpointEmbeddings class from langchain to provide a custom embedding function
class SagemakerEndpointEmbeddingsJumpStart(SagemakerEndpointEmbeddings):
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
        logger.info(f"Embedding {len(texts)} documents took {time_taken} seconds")
        return results

# class for serializing/deserializing requests/responses to/from the embeddings model
class ContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs={}) -> bytes:

        input_str = json.dumps({"text_inputs": prompt, **model_kwargs})
        return input_str.encode('utf-8') 

    def transform_output(self, output: bytes) -> str:

        response_json = json.loads(output.read().decode("utf-8"))
        embeddings = response_json["embedding"]
        if len(embeddings) == 1:
            return [embeddings[0]]
        return embeddings


def create_sagemaker_embeddings_from_js_model(embeddings_model_endpoint_name: str, aws_region: str) -> SagemakerEndpointEmbeddingsJumpStart:
    # all set to create the objects for the ContentHandler and 
    # SagemakerEndpointEmbeddingsJumpStart classes
    content_handler = ContentHandler()

    # note the name of the LLM Sagemaker endpoint, this is the model that we would
    # be using for generating the embeddings
    embeddings = SagemakerEndpointEmbeddingsJumpStart( 
        endpoint_name=embeddings_model_endpoint_name,
        region_name=aws_region, 
        content_handler=content_handler
    )
    return embeddings