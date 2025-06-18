## This is a sample code which demonstrates on how multiple LLM providers can be accessed"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_router import response_huggingface, response_gemini, response_anthrophic, response_groq, response_cohere

app = FastAPI()

# 📦 Input schema
class QueryRequest(BaseModel):
    query: str


CUSTOM_PROMPT_TEMPLATE = """
Response well as per the question asked

Question: {question}

"""

@app.post("/ask")
def ask(request: QueryRequest):
    try:
        HUGGINGFACE_REPO_ID = "Qwen/Qwen2.5-Coder-32B-Instruct"
        result = response_huggingface(
            query=request.query,
            prompt_template=CUSTOM_PROMPT_TEMPLATE,
            repo_id=HUGGINGFACE_REPO_ID
        )

    try:
        result = response_gemini(
            query=request.query,
            prompt_template=CUSTOM_PROMPT_TEMPLATE
        )

    try:
        result = response_anthrophic(
            query=request.query,
            prompt_template=CUSTOM_PROMPT_TEMPLATE
        )

    try:
        model = "llama3-70b-8192"
        result = response_groq(
            query=request.query,
            prompt_template=CUSTOM_PROMPT_TEMPLATE,
            model=model
        )


    try:
         model = "command-r-plus"
         result = response_cohere(
             query=request.query,
             prompt_template=CUSTOM_PROMPT_TEMPLATE,
             model=model

        )
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

