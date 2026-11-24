from fastapi import APIRouter
from app.schemas.analysis import MatchAnalysisRequest, MatchAnalysisResponse
from app.services.matcher_service import analyze_resume_against_job

router = APIRouter()

@router.post("/match", response_model=MatchAnalysisResponse, summary="Compare resume with job description")
def match_resume_to_job(request: MatchAnalysisRequest):
    """Analyze resume against job description, returning match percentage, missing skills, and suggestions."""
    return analyze_resume_against_job(
        resume_text=request.resume_text,
        job_description=request.job_description,
    )

