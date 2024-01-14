PRIMER = "You are an efficient and concise programming assistant that only responds in code."
GENERATE_DIFF = "Write a unified github diff that applies the following changes to {}:\n{}"
REFLECT = "Can you generate an even more accurate, efficient, and concise diff? If not, return 'stop'"

MAX_ITERATIONS = 5
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
        model="gpt-3.5-turbo",
        messages=messages
    )
    content = response.choices[0].message.content
    messages.append({"role": Role.ASSISTANT, "content": content})
    print(content)
    return content

async def get_unified_diff(repo_url, prompt):
    messages.append({"role": Role.USER, "content": GENERATE_DIFF.format(repo_url, prompt)})
    return await prompt_gpt()

async def reflect():
    messages.append({"role": Role.USER, "content": REFLECT})
    return await prompt_gpt()
    

@app.post("/generate-diff/", response_model=ResponseModel)
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
    
@app.get("/health/")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)