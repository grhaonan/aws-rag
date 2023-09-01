from fastapi import APIRouter

router = APIRouter()

@router.post("/text2text")
async def llm_text2text():
    return {"message": "Hello FastAPI! text2text"}


@router.post("/rag")
async def llm_rag():
    return {"message": "Hello FastAPI! rag"}
