from fastapi import APIRouter, HTTPException, status
from app.schemas.llm_analysis import LLMAnalysisRequest, LLMAnalysisResponse
from app.services.llm_service import analyze_resume_with_llm

router = APIRouter()

@router.post(
    "/analyze",
    response_model=LLMAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate personalized resume improvements, rewritten bullet points, and section feedback using LLM",
)
def analyze_resume_with_llm_endpoint(request: LLMAnalysisRequest):
    """
    Step 10: LLM API Integration Endpoint.
    
    1. Analyzes uploaded resume text against the target job description.
    2. Generates personalized resume improvement suggestions.
    3. Rewrites existing resume bullet points using professional action verbs.
    4. Suggests relevant missing keywords from the job description.
    5. Audits weak sections and provides actionable fixes.
    6. Strictly adheres to grounding constraints (never invents skills, experiences, or numbers).
    7. Uses environment variables from `.env` (Gemini, OpenAI, or grounded fallback).
    """
    if not request.resume_text or not request.resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text cannot be empty. Please provide valid extracted resume text.",
        )

    if not request.job_description or not request.job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description cannot be empty. Please provide target job description text.",
        )

    try:
        response = analyze_resume_with_llm(
            resume_text=request.resume_text,
            job_description=request.job_description,
            resume_sections=request.resume_sections,
            job_title=request.job_title or "",
            missing_skills=request.missing_skills or [],
        )
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the resume with the LLM: {str(e)}",
        )

