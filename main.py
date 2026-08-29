import re
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from io import BytesIO
# from dotenv import load_dotenv
# from openai import OpenAI
# import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes

import platform

if platform.system() == "Windows":    
   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#load_dotenv()



#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# @app.get("/")
# def home():
#     return {"message": "AI Resume Analyzer API is running!"}


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...), job_description: str = Form("")):
    print("UPLOAD REQUEST RECEIVED")
    #print("JOB DESCRIPTION:", job_description)

    filename = file.filename.lower()
    
    if not filename.endswith((".pdf", ".jpg", ".jpeg", ".png")):
        return {"error": "Please upload a PDF, JPG, JPEG, or PNG file."}

    contents = await file.read()

    if not contents:
        return {"error": "The uploaded file is empty."}

    

    

    text = ""

    if filename.endswith(".pdf"):
        pdf = PdfReader(BytesIO(contents))
        # First try normal PDF text extraction
        for page in pdf.pages:
            text += page.extract_text() or ""

    else:
        # JPG / JPEG / PNG
        image = Image.open(BytesIO(contents))
        text = pytesseract.image_to_string(image)

    # If very little text was extracted from pdf, use OCR
    if filename.endswith(".pdf") and len(text.strip()) < 50:
       print("Normal extraction failed. Using OCR...")

    if platform.system() == "Windows":
       images = convert_from_bytes(
          contents,
          poppler_path=r"C:\Users\DEVANSH\Downloads\Release-25.02.0-0\poppler-25.02.0\Library\bin"
       )
    else:
        images = convert_from_bytes(contents)
       
    text = ""

    for image in images:
           text += pytesseract.image_to_string(image)

    print("EXTRACTED TEXT:")
    print(text)

    text_lower = text.lower()

    sections = {
    "skills": any(word in text_lower for word in [
        "skills", "technical skills", "core skills"
    ]),

    "education": any(word in text_lower for word in [
        "education", "academic", "qualification"
    ]),

    "experience": any(word in text_lower for word in [
        "experience", "work experience", "internship",
        "employment", "professional experience"
    ]),

    "projects": any(word in text_lower for word in [
        "projects", "project", "academic projects",
        "personal projects"
    ]),

    "certifications": any(word in text_lower for word in [
        "certifications", "certification", "certificates",
        "certificate"
    ])
}
        
        
        
        
        
    

    skills_list = [
    # Programming
    "python", "java", "c", "c++", "c#",
    "javascript", "typescript",

    # Web
    "html", "css", "react", "node.js",
    "express", "django", "flask", "fastapi",

    # Databases
    "sql", "mysql", "postgresql", "mongodb",

    # AI / Data Science
    "machine learning", "deep learning",
    "data science", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch",

    # Tools
    "git", "github", "docker", "linux",

    # Cloud
    "aws", "azure", "google cloud"
]
        
        

        
    

    found_skills = []

    for skill in skills_list:
        if skill in ["c++", "c#", "node.js"]:
            if skill in text_lower:
                found_skills.append(skill)
        else:
            pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    skill_score = min(len(found_skills) * 5, 30)

    education_score = 15 if sections["education"] else 0
    experience_score = 20 if sections["experience"] else 0
    projects_score = 20 if sections["projects"] else 0
    certification_score = 10 if sections["certifications"] else 0
    quality_score = 5 if len(text.strip()) >= 300 else 0

    resume_score = (
        skill_score
        + education_score
        + experience_score
        + projects_score
        + certification_score
        + quality_score
    )

    job_text = job_description.lower()

    job_skills = []

    for skill in skills_list:
        if skill in ["c++", "c#", "node.js"]:
            if skill in job_text:
                job_skills.append(skill)
        else:
            pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, job_text):
            job_skills.append(skill)

    job_skills = list(dict.fromkeys(job_skills))

    #print("JOB SKILLS:", job_skills)

    matching_skills = [
        skill for skill in found_skills
        if skill in job_skills
    ]

    missing_job_skills = [
        skill for skill in job_skills
        if skill not in found_skills
    ]

    if len(job_skills) > 0:
        job_match_score = round(
            (len(matching_skills) / len(job_skills)) * 100
        )
    else:
        job_match_score = 0

    if job_match_score >= 75:
        match_label = "Scoring Match"
    elif job_match_score >= 50:
        match_label = "Moderate Match"
    else:
        match_label = "Low Match"


        
        
    
    missing_sections = []

    if not sections["education"]:
        missing_sections.append("Education")

    if not sections["experience"]:
        missing_sections.append("Experience")

    if not sections["projects"]:
        missing_sections.append("Projects")

    if not sections["certifications"]:
        missing_sections.append("Certifications")

    suggestions = []

    
    if "Education" in missing_sections:
        suggestions.append("Add an Education section to your resume.")

    if "Experience" in missing_sections:
        suggestions.append("Add relevant work or internship experience if applicable.")

    if "Projects" in missing_sections:
        suggestions.append("Add relevant projects to demonstrate your practical skills.")

    if "Certifications" in missing_sections:
        suggestions.append("Add relevant certifications if you have them.")

    if len(found_skills) < 5:
        suggestions.append("Consider adding more relevant technical skills to your resume.")

        
    if missing_job_skills:
        for skill in missing_job_skills:
            suggestions.append(f"Consider learning or adding {skill} to improve your job match.")

    return {
        "filename": file.filename,
        "sections_found": sections,
        "found_skills": found_skills,
        "skill_score": skill_score,
        "resume_score": resume_score,
        "missing_sections": missing_sections,
        "suggestions": suggestions,
        "job_match_score": job_match_score,
        "job_skills": job_skills,
        "matching_skills": matching_skills,
        "missing_job_skills": missing_job_skills,
        "match_label": match_label,
        "text": text[:2000]
    }

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")