from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import json
import os

app = FastAPI(title="AppCompiler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompileRequest(BaseModel):
    prompt: str
    api_key: str

@app.get("/")
async def root():
    return {"message": "AppCompiler is running"}

@app.post("/compile")
async def compile_app(request: CompileRequest):
    client = anthropic.Anthropic(api_key=request.api_key)
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system="You are an app compiler. Convert user descriptions into JSON with db_schema, api_schema, ui_schema, auth_schema. Return valid JSON only.",
        messages=[{"role": "user", "content": request.prompt}]
    )
    
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
