from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.dashboard import DashboardAnalysisRequest, DashboardAnalysisResponse
from app.services.dashboard_service import compute_full_dashboard_analysis
from app.db.mongodb import get_database
from app.api.deps import get_optional_current_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.post(
    "/summary",
    response_model=DashboardAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute comprehensive dashboard summary with ATS score, experience/education matching, and summary/project improvements",
)
def get_dashboard_summary_endpoint(
    request: DashboardAnalysisRequest,
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    db=Depends(get_database),
):
    """
    Step 11 & 12: Compute Dashboard Analysis
    - Overall match percentage (0-100)
    - Matched & missing skills
    - Experience matching (candidate vs required)
    - Education matching (candidate vs required)
    - ATS score breakdown & grade
    - AI suggestions for summary & projects
    """
    if not request.resume_text or not request.resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text cannot be empty.",
        )
    if not request.job_description or not request.job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description cannot be empty.",
        )

    try:
        response = compute_full_dashboard_analysis(
            resume_text=request.resume_text,
            job_description=request.job_description,
            resume_sections=request.resume_sections,
            required_skills=request.required_skills,
            preferred_skills=request.preferred_skills,
            job_title=request.job_title,
            required_experience=request.required_experience,
            education_requirements=request.education_requirements,
        )

        # Save record in MongoDB linked to user ID if authenticated
        if current_user:
            try:
                db.analyses.insert_one({
                    "user_id": current_user.id,
                    "resume_filename": "Uploaded_Resume.pdf",
                    "job_title": request.job_title or "Target Role",
                    "overall_match_percentage": response.overall_match_percentage,
                    "ats_score": response.ats_score.overall_ats_score,
                    "ats_grade": response.ats_score.grade,
                    "matched_skills": [f"Total: {response.matched_skills_count}"],
                    "missing_skills": [f"Total: {response.missing_skills_count}"],
                    "summary_text": response.summary_improvement.improved_summary,
                    "report_data": response.model_dump(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                pass

        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard analysis: {str(e)}",
        )

