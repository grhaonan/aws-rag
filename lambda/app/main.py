import sys
import subprocess
from mangum import Mangum
from fastapi import FastAPI
from routers.api_v1.api import router

app = FastAPI()

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API for questions answering system"}

handler = Mangum(app=app)