from .fastapi_request import Request, VectorDBType
from .initialise import (load_vector_db_opensearch, 
                         setup_sagemaker_endpoint_for_text_generation)
from fastapi import APIRouter
from typing import Any, Dict
import os
from langchain.chains.question_answering import load_qa_chain
from .sm_helper import query_sm_endpoint


logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()


VECTOR_DB_DIR = os.path.join("/tmp", "_vectordb")

_vector_db = None
_current_vectordb_type = None
_sm_llm = None

router = APIRouter()

opensearch_secret = os.environ.get('OPENSEARCH_SECRET')
region = os.environ.get('REGION')


def _init(req:Request):
    global _vector_db
    global _current_vectordb_type
    logger.info(f"req.vector_db_type: {req.vector_db_type}, _vector_db: {_vector_db}")
    if req.vectordb_type != _current_vectordb_type:
        logger.info(f"req.vectordb_type={req.vectordb_type} does not match _current_vectordb_type={_current_vectordb_type}, "
                    f"resetting _vector_db")
        _vector_db = None
    if req.vectordb_type == VectorDBType.opensearch and _vector_db is None:
        # ARN of the secret is of the following format arn:aws:secretsmanager:region:account_id:secret:my_path/my_secret_name-autoid
        os_creds_secretid_in_secrets_manager = "-".join(os.environ.get('OPENSEARCH_SECRET').split(":")[-1].split('-')[:-1])
        _vector_db = load_vector_db_opensearch(req.vectordb_s3_path,
                                               VECTOR_DB_DIR,
                                               req.embeddings_generation_model,
                                               region)
    elif _vector_db is None:
        logger.info(f"db already initialized, skipping")
    else：
        logger.error(f"req.vectordb_type={req.vectordb_type} which is not supported, _vector_db={_vector_db}")



    # similar to the above, but for the sagemaker endpoint

    global _sm_llm
    if _sm_llm is None:
        logger.info(f"SM LLM endpoint is not setup, setting it up")
        _sm_llm = setup_sagemaker_endpoint_for_text_generation(req,region)
        logger.info("setting up sagemaker llm endpoint")
    else:
        logger.info(f"SM LLM endpoint is already setup, skipping")


@router.post("/text2text")
async def llm_text2text(req: Request) -> Dict[str, Any]:
    # debugdding request
    logger.info(f"req: {req}")

    _init(req)

    answer = query_sm_endpoint(req)
    resp = {'question': req.q, 'answer': answer}
    return {"message": "Hello FastAPI! text2text"}


@router.post("/rag")
async def llm_rag(req: Request) -> Dict[str, Any]:
    # debugdding request
    logger.info(f"req: {req}")

   # initialize the vector db and the sagemaker endpoint
   # it will be saved to gloabl  variable
    _init(req)

    # Use the vector db to find similar documents to the query
    # the vector db call would automatically convert the query text
    # into embeddings
    
    docs = _vector_db.similarity_search(req.q, k=req.max_matching_docs)
    logger.info(f"there are the {req.max_matching_docs} closest documents to the query= \"{req.q}\"")
    for doc in docs:
        logger.info(f"--------")
        logger.info(f"doc: {doc}")
        logger.info(f"--------")
    
    #define prompt
    prompt_template = """Answer based on context:\n {context} \n Question: {question} \n Answer:"""
    logger.info(f"prompt sent to llm = \"{prompt_template}\"")
    chain = load_qa_chain(llm=_sm_llm, prompt=prompt_template)
    answer = chain({"input_document": docs, "question": req.q}, return_only_output=True)['output_text']
    logger.info(f"answer received from llm,\nquestion: \"{req.q}\"\nanswer: \"{answer}\"")
    resp  = {'question': req.q, 'answer': answer}
    if req.verbose:
        resp['docs'] = docs
    return {"message": "Hello FastAPI! rag"}


