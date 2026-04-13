import asyncio
from datetime import datetime
from uuid import uuid4
from app.schemas.resume import ResumeBase

# Mock resume dict similar to what SQLAlchemy returns
resume_dict = {
    "id": uuid4(),
    "user_id": uuid4(),
    "file_name": "test.pdf",
    "file_url": "test.pdf",
    "file_size": 100,
    "uploaded_at": datetime.now(),
    "status": "completed",
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "extracted_text": None,
    "extracted_skills": None,  # SQLAlchemy might return None for JSONB fields before populated
    "education": None,
    "experience": None,
    "extra_metadata": None,
    "seniority_level": None,
    "years_of_experience": None,
    "career_trajectory": None,
    "domain_expertise": None,
    "impact_metrics": None,
    "context_aware_skills": None,
    "resume_analysis": None,
    "analysis_version": None,
}

try:
    print("Validating dict...")
    ResumeBase.model_validate(resume_dict)
    print("Success dict!")
except Exception as e:
    print(e)
