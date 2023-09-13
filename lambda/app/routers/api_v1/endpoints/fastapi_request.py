import os
import boto3
from enum import Enum
from pydntic import BaseModel


# fetch value from aws parameter store
ssm = boto3.client('ssm')
region = ssm.get_parameter(Name='REGION', WithDecryption=True)['Parameter']['Value']
text2text_endpoint_name = ssm.get_parameter(Name='TEXT2TEXT_ENDPOINT_NAME', WithDecryption=True)['Parameter']['Value']
sagemaker_endpoint_name = ssm.get_parameter(Name='SAGEMAKER_ENDPOINT_NAME', WithDecryption=True)['Parameter']['Value']


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
    Text2TextModelName.flan_t5_xxl: text2text_endpoint_name,
    EmbeddingsModelName.gpt_j_6b: sagemaker_endpoint_name
}