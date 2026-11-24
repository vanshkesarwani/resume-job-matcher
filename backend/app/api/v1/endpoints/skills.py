from fastapi import APIRouter, HTTPException
from app.schemas.skills import SkillMatchRequest, SkillMatchResponse
from app.services.skill_matcher_service import match_skills

router = APIRouter()

@router.post(
    "/match",
    response_model=SkillMatchResponse,
    summary="Match resume skills against job description with synonym support",
)
def match_resume_skills(request: SkillMatchRequest):
    """
    Compares candidate skills against job requirements:
    - Normalizes similar skill names and aliases (e.g., JS = JavaScript, TS = TypeScript, K8s = Kubernetes).
    - Categorizes matching vs missing skills into required and preferred groups.
    - Highlights additional candidate competencies not explicitly requested.
    - Computes required, preferred, and overall match percentages.
    """
    # Validation
    has_candidate_info = bool(request.resume_skills or (request.resume_text and request.resume_text.strip()))
    has_job_info = bool(
        request.required_skills
        or request.preferred_skills
        or (request.job_description and request.job_description.strip())
    )

    if not has_candidate_info:
        raise HTTPException(
            status_code=400,
            detail="Missing candidate skills. Please provide either 'resume_skills' list or 'resume_text'.",
        )

    if not has_job_info:
        raise HTTPException(
            status_code=400,
            detail="Missing job requirements. Please provide 'required_skills' list or 'job_description' text.",
        )

    try:
        response = match_skills(request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during skill matching: {str(e)}",
        )

