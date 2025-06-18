import os
import requests
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import google.generativeai as genai
import anthropic
import cohere
from dotenv import load_dotenv

load_dotenv()


def load_llm(repo_id: str, token: str):
    return HuggingFaceEndpoint(
        repo_id=repo_id,
        task="text-generation",
        huggingfacehub_api_token=token,
        max_new_tokens=512,
        temperature=0.7
    )

def response_huggingface(query: str, prompt_template: str, repo_id: str):
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HF Token is not set!")
    else:
        HuggingFace_REPO_ID = repo_id
        prompt = PromptTemplate(template=prompt_template, input_variables=["question"])
        formatted_prompt = prompt.format(question=query)
        llm = load_llm(HuggingFace_REPO_ID, HF_TOKEN)
        try:
            response = llm.invoke(formatted_prompt)
            return response
        except Exception as e:
            return f"Error: {str(e)}"

def response_gemini(query: str, prompt_template: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Google API Key not set!")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
    prompt = prompt_template.format(question=query)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# def response_anthrophic(query: str, prompt_template: str) -> str:
#     client = anthropic.Anthropic(api_key=os.getenv("ANTHROPHIC_API_KEY"))
#     final_prompt = prompt_template.format(question=query)
#     try:
#         response = client.messages.create(
#             model="claude-3-opus-20240229",
#             max_tokens=512,
#             messages=[
#                 {"role": "user", "content": final_prompt}
#             ]
#         )
#         return response.content[0].text.strip() if response.content else "No response from Claude."
#     except Exception as e:
#         return f"Error: {str(e)}"


def response_anthrophic(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPHIC_API_KEY"))
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip() if response.content else "No response from Claude."
    except Exception as e:
        return f"Error: {str(e)}"



def response_groq(query: str, prompt_template: str, model: str) -> str:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in environment variables")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = prompt_template.replace("{question}", query)
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"


def response_cohere(query:str, prompt_template: str, model: str) -> str:
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise ValueError("COHERE_API_KEY not set in .env")

    co = cohere.Client(api_key)

    prompt = prompt_template.replace("{question}", query)

    try:
        response = co.chat(
            model=model,
            message=prompt,
            temperature=0.7
        )
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"