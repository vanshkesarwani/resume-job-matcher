from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.job import JobExtractRequest, JobExtractResponse
from app.services.job_extractor_service import parse_and_store_job_description
from app.db.mongodb import get_database
from app.api.deps import get_optional_current_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.post(
    "/extract",
    response_model=JobExtractResponse,
    summary="Extract structured requirements and skills from a Job Description",
)
def extract_job_description(
    request: JobExtractRequest,
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    db=Depends(get_database),
):
    """
    Extracts key information from job description:
    - Required Skills
    - Preferred Skills
    - Required Years of Experience
    - Education Requirements
    - Job Title
    - Key Responsibilities
    Persists data securely for future matching and returns structured JSON.
    """
    if not request.job_description or not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty. Please paste the job requirements.",
        )

    if len(request.job_description.strip()) < 15:
        raise HTTPException(
            status_code=400,
            detail="Job description is too brief. Please provide a more detailed job posting.",
        )

    try:
        response = parse_and_store_job_description(request.job_description)

        # Save record in MongoDB linked to user ID if authenticated
        if current_user:
            try:
                db.jobs.insert_one({
                    "user_id": current_user.id,
                    "job_title": response.job_title,
                    "job_description": request.job_description.strip(),
                    "required_skills": response.required_skills,
                    "preferred_skills": response.preferred_skills,
                    "required_experience": response.required_experience,
                    "education_requirements": response.education_requirements,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                pass

        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during job description extraction: {str(e)}",
        )

