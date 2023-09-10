import os
import boto3
from enum import Enum
from pydntic import BaseModel



ACCOUNT_ID = boto3.client('sts').get_caller_identity().get('Account')
REGION = boto3.Session().region_name

class Text2TextModelName(str, Enum):
    flan_t5_xxl = "flan-t5-xxl"

class EmbeddingsModelName(str, Enum):
    gpt_j_6b = "gpt-j-6b"


class VectorDBType(str, Enum):
    opensearch = "opensearch"

class Request(BaseModel):
    q: str
    max_length: int = 500
    num_return_sequences: int = 1
    top_k: int = 250
    top_p: float = 0.95
    do_sample: bool = False
    temperature: float = 1
    verbose: bool = False
    max_matching_docs: int = 3  
    text_generation_model: Text2TextModelName = Text2TextModelName.flan_t5_xxl
    embeddings_generation_model: EmbeddingsModelName = EmbeddingsModelName.gpt_j_6b
    vectordb_type: VectorDBType = VectorDBType.opensearch
    vectordb_s3_path: str = f""


sagemaker_endpoint_mapping = {
    Text2TextModelName.flan_t5_xxl: os.environ.get('TEXT2TEXT_ENDPOINT_NAME'),
    EmbeddingsModelName.gpt_j_6b: os.environ.get('SAGEMAKER_ENDPOINT_NAME')
}