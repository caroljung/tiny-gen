import asyncio
import logging
from enum import Enum
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .clients.supabase_client import SupabaseClient, DiffQuery, DiffResponse
from .clients.openai_client import GptClient, GPT_MODEL
from .utils.repo_parser import scrape_github_repository
from .utils.prompts import *

app = FastAPI()
gpt = GptClient()
supabase = SupabaseClient()
logger = logging.getLogger('tiny-gen-logger')

class RequestModel(BaseModel):
    repoUrl: str
    prompt: str

async def generate(repo_url, prompt):
    try:
        # Store api query
        diff_query = await supabase.store_diff_query(DiffQuery(repo_url=repo_url, prompt=prompt, gpt_model=GPT_MODEL))
        repo_content = scrape_github_repository(repo_url)
        
        # Stream gpt's response
        diff_response = DiffResponse(
            query_id=diff_query.id,
            diff="")         
        async for chunk in await gpt.get_unified_diff(repo_content, prompt):
            if chunk.choices[0].finish_reason == STOP_TOKEN:
                break
            else:
                streaming_bytes = chunk.choices[0].delta.content
                diff_response.diff += streaming_bytes
                logging.info(streaming_bytes)
                yield streaming_bytes
            
        gpt.save_response(diff_response.diff)
        
        # Stream reflection
        updated_diff = ""
        async for chunk in await gpt.reflect():
            if chunk.choices[0].finish_reason == STOP_TOKEN or chunk.choices[0].delta.content == STOP_TOKEN:
                break
            else:
                streaming_bytes = chunk.choices[0].delta.content
                updated_diff += streaming_bytes
                logging.info(streaming_bytes)
                yield streaming_bytes
        
        # Store api response
        diff_response.diff = updated_diff if len(updated_diff) > 0 else diff_response.diff
        await supabase.store_diff_response(diff_response)

    except Exception as e:
        yield str(e)

@app.post("/api/generate-diff")
async def generate_diff(request_data: RequestModel):
    repo_url = request_data.repoUrl
    prompt = request_data.prompt
    
    if not repo_url:
        return "Missing repository url"
    if not prompt:
        return "Missing prompt"
    return StreamingResponse(generate(repo_url, prompt), media_type='text/event-stream')

@app.get("/api/health")
def hello_world():
    return {"status": "healthy :)"}

async def fake_data_streamer():
    for i in range(10):
        yield b'some fake data!\n\n'
        await asyncio.sleep(0.5)
    
@app.post("/api/stream")
async def stream_data():
    return StreamingResponse(fake_data_streamer(), media_type='text/event-stream')
