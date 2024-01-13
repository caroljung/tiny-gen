from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()
client = OpenAI()

text_diff_prompt = "Generate a unified github diff that applies the following changes to {}:\n{}"

class RequestModel(BaseModel):
    repoUrl: str
    prompt: str

class ResponseModel(BaseModel):
    unified_diff: str

async def get_unified_diff(repo_url, prompt, max_tokens=200, timeout=30):
    # Use OpenAI API to apply the prompt to the unified diff
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": text_diff_prompt.format(repo_url, prompt)}
        ]
    )

    return response.choices[0].message.content


@app.post("/generate-diff/", response_model=ResponseModel)
async def generate_diff(request_data: RequestModel):
    repo_url = request_data.repoUrl
    prompt = request_data.prompt

    try:
        unified_diff = await get_unified_diff(repo_url, prompt)
        return {"unified_diff": unified_diff}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health/")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)