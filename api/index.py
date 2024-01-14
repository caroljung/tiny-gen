PRIMER = "You are an efficient and concise programming assistant that reads code from links to github repositories and produces code diffs based on a given prompt."
GENERATE_DIFF = "Write a unified github diff applied to code in this github repository {}. The code diff should alter the existing code in the respository following the given textual command: '{}'. Make sure to reference all file paths relative to the repository's root directory. The diff should strictly apply changes to existing code in the given repository."
REFLECT = "Can you generate an even more accurate, efficient, and concise diff? If not, return 'stop'"
READ_CODE="Read the first four lines of code in file {} in this repository {}"

MAX_ITERATIONS = 2
STOP_TOKEN = 'stop'

from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()
client = OpenAI()
messages = []

class Role(str, Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class RequestModel(BaseModel):
    repoUrl: str
    prompt: str

class ResponseModel(BaseModel):
    unified_diff: str
    
def reset_messages():
    messages.clear()
    messages.append({"role": Role.SYSTEM, "content": PRIMER})

async def prompt_gpt():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    content = response.choices[0].message.content
    messages.append({"role": Role.ASSISTANT, "content": content})
    print(content)
    return content

async def read_code(repo_url, prompt):
    messages.append({"role": Role.USER, "content": READ_CODE.format(repo_url, prompt)})
    return await prompt_gpt()

async def get_unified_diff(repo_url, prompt):
    messages.append({"role": Role.USER, "content": GENERATE_DIFF.format(repo_url, prompt)})
    return await prompt_gpt()

async def reflect():
    messages.append({"role": Role.USER, "content": REFLECT})
    return await prompt_gpt()
    

@app.post("/api/generate-diff", response_model=ResponseModel)
async def generate_diff(request_data: RequestModel):
    repo_url = request_data.repoUrl
    prompt = request_data.prompt

    reset_messages()

    try:
        unified_diff = await get_unified_diff(repo_url, prompt)
        
        for i in range(MAX_ITERATIONS):
            reflection = await reflect()
            if reflection.lower() == STOP_TOKEN:
                break
            else:
                unified_diff = reflection
            
        return {
            "unified_diff": unified_diff,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/read-repo")
async def read_repo(request: RequestModel):
    return await read_code(request.repoUrl, request.prompt)
    
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}
