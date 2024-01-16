MAX_REFLECTION_COUNT = 1
STOP_TOKEN = "stop"
GPT_MODEL = "gpt-4-1106-preview"

import logging
from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from .clients.supabase_client import SupabaseClient, DiffQuery, DiffResponse
from .utils.repo_parser import scrape_github_repository
from .utils.prompts import *

app = FastAPI()
gpt = OpenAI()
supabase = SupabaseClient()
messages = []
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


async def prompt_gpt():
    response = gpt.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    )
    content = response.choices[0].message.content
    messages.append({"role": Role.ASSISTANT, "content": content})
    print(content)
    return content

async def read_code(repo_content):
    messages.append({"role": Role.USER, "content": READ_CODE.format(repo_content)})
    return await prompt_gpt()

async def get_unified_diff(repo_content, prompt):
    messages.clear()
    messages.append({"role": Role.SYSTEM, "content": PRIMER})
    messages.append({"role": Role.USER, "content": GENERATE_DIFF.format(repo_content, prompt)})
    return await prompt_gpt()

async def reflect():
    messages.append({"role": Role.USER, "content": REFLECT})
    return await prompt_gpt()
    

@app.post("/api/generate-diff", response_model=ResponseModel)
async def generate_diff(request_data: RequestModel):
    repo_url = request_data.repoUrl
    prompt = request_data.prompt

    try:
        diff_query = supabase.store_diff_query(DiffQuery(repo_url=repo_url, prompt=prompt, gpt_model=GPT_MODEL))
        repo_content = scrape_github_repository(repo_url)
        unified_diff = await get_unified_diff(repo_content, prompt)
        diff_response = DiffResponse(
            query_id=diff_query.id,
            diff=unified_diff,
            reflection_count=0)

        for i in range(MAX_REFLECTION_COUNT):
            reflection = await reflect()
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
    return await read_code(repo_content)
    
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}
