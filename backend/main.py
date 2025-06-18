# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from pydantic import BaseModel
# from process_file import extract_pdf, extract_docs, extract_image
# from llm_router import response_anthrophic
# app = FastAPI()
#
# class JD(BaseModel):
#     Job_description: str
#
# PROMPT_TEMPLATE = """
# You are an AI assistant that evaluates resumes based on job descriptions. Given the resume content and job description, perform the following:
#
# 1. Score the resume for the job (out of 100).
# 2. 2–5 points highlighting the candidate’s strengths.
# 3. Analyze keywords: list matched and missing ones.
# 4. Suggest improvements to resume sections (experience, projects, skills, education).
#
# Respond strictly in this JSON format:
#
# {{
#   "score": <integer>,
#   "strengths": ["<point1>", "<point2>"],
#   "keyword_analysis": {{
#     "matched_keywords": ["<keyword1>", "<keyword2>"],
#     "missing_keywords": ["<keyword1>", "<keyword2>"]
#   }},
#   "improvement_suggestions": {{
#     "Experience": ["<point1>", "<point2>"],
#     "Projects": ["<point1>", "<point2>"],
#     "Skills": ["<point1>", "<point2>"],
#     "Education": ["<point1>", "<point2>"]
#   }}
# }}
#
# Resume:
# {resume}
#
# Job Description:
# {job_description}
# """
#
#
#
#
# @app.post("/analyze")
# async def analyze_resume(file: UploadFile = File(...), job_description: str = Form(...)):
#     if file.filename.endswith(".pdf"):
#         content = extract_pdf(file.file)
#     elif file.filename.endswith(".docx"):
#         content = extract_docs(file.file)
#     elif file.filename.endswith(".png") or file.filename.endswith(".jpg"):
#         content = extract_image(file.file)
#     else:
#         return {"Un supported file format uploaded!"}
#
#     if not job_description:
#         return {"error": "Job description is required"}
#     final_prompt = PROMPT_TEMPLATE.format(resume=content, job_description=job_description)
#
#     response = response_anthrophic(job_description, final_prompt)
#
#     return {"result": response}
#
#
import os
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from process_file import extract_pdf, extract_docs, extract_image
from llm_router import response_anthrophic  # Ensure this function is correctly defined in llm_router.py

app = FastAPI()

# CORS (allow all origins for now; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic response model
class ResumeAnalysisResponse(BaseModel):
    score: int
    strengths: List[str]
    keyword_analysis: Dict[str, List[str]]
    improvement_suggestions: Dict[str, List[str]]

# Prompt Template (escaped with double curly braces)
PROMPT_TEMPLATE = """
You are an AI assistant that evaluates resumes based on job descriptions. Given the resume content and job description, perform the following:

1. Score the resume for the job (out of 100).
2. 2–5 points highlighting the candidate’s strengths.
3. Analyze keywords: list matched and missing ones.
4. Suggest improvements to resume sections (experience, projects, skills, education).

Respond strictly in this JSON format:

{{
  "score": <integer>,
  "strengths": ["<point1>", "<point2>"],
  "keyword_analysis": {{
    "matched_keywords": ["<keyword1>", "<keyword2>"],
    "missing_keywords": ["<keyword1>", "<keyword2>"]
  }},
  "improvement_suggestions": {{
    "Experience": ["<point1>", "<point2>"],
    "Projects": ["<point1>", "<point2>"],
    "Skills": ["<point1>", "<point2>"],
    "Education": ["<point1>", "<point2>"]
  }}
}}

Resume:
{resume}

Job Description:
{job_description}
"""

@app.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    # Validate file type
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png",
        "image/jpeg",
    ]:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    # Extract resume content
    try:
        if file.filename.endswith(".pdf"):
            content = extract_pdf(file.file)
        elif file.filename.endswith(".docx"):
            content = extract_docs(file.file)
        elif file.filename.endswith(".png") or file.filename.endswith(".jpg"):
            content = extract_image(file.file)
        else:
            raise HTTPException(status_code=415, detail="Unsupported file extension")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    if not content:
        raise HTTPException(status_code=400, detail="Empty resume content extracted")

    # Format prompt
    final_prompt = PROMPT_TEMPLATE.format(resume=content, job_description=job_description)

    # Get LLM response
    llm_response = response_anthrophic(final_prompt)

    # Parse JSON response
    try:
        response_data = json.loads(llm_response)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"LLM returned invalid JSON: {llm_response}")

    return response_data


@app.get("/health")
def health_check():
    return {"status": "ok"}
