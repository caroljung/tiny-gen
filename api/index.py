MAX_REFLECTION_COUNT = 1
STOP_TOKEN = "stop"
GPT_MODEL = "gpt-4-1106-preview"

import logging
from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .clients.supabase_client import SupabaseClient, DiffQuery, DiffResponse
from .clients.openai_client import GptClient
from .utils.repo_parser import scrape_github_repository
from .utils.prompts import *

app = FastAPI()
gpt = GptClient()
supabase = SupabaseClient()
logger = logging.getLogger('tiny-gen-logger')

class Role(str, Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class RequestModel(BaseModel):
    repoUrl: str
    prompt: str

class ResponseModel(BaseModel):
    unified_diff: str

@app.post("/api/generate-diff", response_model=ResponseModel)
async def generate_diff(request_data: RequestModel):
    repo_url = request_data.repoUrl
    prompt = request_data.prompt

    try:
        diff_query = supabase.store_diff_query(DiffQuery(repo_url=repo_url, prompt=prompt, gpt_model=GPT_MODEL))
        repo_content = scrape_github_repository(repo_url)
        unified_diff = await gpt.get_unified_diff(repo_content, prompt)
        diff_response = DiffResponse(
            query_id=diff_query.id,
            diff=unified_diff,
            reflection_count=0)

        for i in range(MAX_REFLECTION_COUNT):
            reflection = await gpt.reflect()
            if reflection.lower() == STOP_TOKEN:
                break
            else:
                diff_response.reflection_count += 1
                unified_diff = reflection
                
        supabase.store_diff_response(diff_response)

        return { "unified_diff": unified_diff }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/read-repo")
async def read_repo(request: RequestModel):
    repo_content = scrape_github_repository(request.repoUrl)
    logger.info(repo_content)
    return await gpt.read_code(repo_content)
    
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}
