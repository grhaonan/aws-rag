import boto3
import json
import logging
from typing import List, Dict
from .fastapi_request import(Request,
                             sagemaker_endpoint_mapping)

logger = logging.getLogger(__name__)
def query_llm(encode_json, endpoint_name) -> Dict:
    content_type="application/json"
    client = boto3.client('runtime.sagemaker')
    response = client.invoke_endpoint(EndpointName=endpoint_name,
        ContentType=content_type,
        Body=encode_json)
    return response


def parse_response_model_flan_t5(query_response) -> List:
    model_predictions = json.loads(query_response["Body"].read())
    logger.info(f"model_predictions are: {model_predictions}")
    generated_text = model_predictions["generated_texts"]
    return generated_text


def query_sm_endpoint(req: Request) -> List:
    payload = {
        "text_inputs": req.query,
        "max_length": req.max_length,
        "num_return_sequences": req.num_return_sequences,
        "top_k": req.top_k,
        "top_p": req.top_p,
        "do_sample": req.do_sample,
        "temperature": req.temperature}
    text_generation_model_endpoint = sagemaker_endpoint_mapping[req.text_generation_model_name]

    query_response = query_llm(encode_json = json.dumps(payload).encode("utf-8"),
        endpoint_name = text_generation_model_endpoint)
    

    generated_texts = parse_response_model_flan_t5(query_response)
    logger.info(f"the generated output is: {generated_texts}")
    return generated_texts