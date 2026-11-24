from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.db.mongodb import get_database
from app.schemas.auth import UserResponse
from app.schemas.user_records import (
    ResumeRecord,
    JobRecord,
    AnalysisRecord,
    SaveAnalysisRequest,
)
from app.services.storage_service import delete_file_permanently
from app.api.deps import get_current_user

router = APIRouter()

def _to_object_id(id_str: str) -> Any:
    """Helper to convert string ID to ObjectId if valid, else returns string."""
    return ObjectId(id_str) if ObjectId.is_valid(id_str) else id_str

# ==============================================================================
# RESUMES
# ==============================================================================
@router.get(
    "/resumes",
    response_model=List[ResumeRecord],
    summary="List all resumes uploaded by the logged-in user",
)
def get_user_resumes(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    cursor = db.resumes.find({"user_id": current_user.id}).sort("created_at", -1)
    results = []
    for doc in cursor:
        results.append(ResumeRecord(
            id=str(doc["_id"]),
            user_id=doc.get("user_id", current_user.id),
            filename=doc.get("filename", "Resume.pdf"),
            file_type=doc.get("file_type", "pdf"),
            file_size=doc.get("file_size", 0),
            detected_skills=doc.get("detected_skills", []),
            raw_text=doc.get("raw_text"),
            created_at=str(doc.get("created_at", "")),
        ))
    return results

@router.delete(
    "/resumes/{resume_id}",
    summary="Permanently delete a resume record and stored file",
)
def delete_user_resume(
    resume_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    query = {"_id": _to_object_id(resume_id), "user_id": current_user.id}
    doc = db.resumes.find_one(query)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or you do not have permission to delete it.",
        )

    # Delete physical file from disk if file_id exists
    file_id = doc.get("file_id")
    if file_id:
        try:
            for p in settings.UPLOAD_DIR.glob(f"{file_id}_*"):
                delete_file_permanently(p)
        except Exception:
            pass

    db.resumes.delete_one(query)
    return {"message": "Resume and stored file permanently deleted successfully"}

@router.delete(
    "/resumes",
    summary="Permanently delete all resumes uploaded by the logged-in user",
)
def delete_all_user_resumes(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    cursor = db.resumes.find({"user_id": current_user.id})
    deleted_count = 0
    for doc in cursor:
        file_id = doc.get("file_id")
        if file_id:
            try:
                for p in settings.UPLOAD_DIR.glob(f"{file_id}_*"):
                    delete_file_permanently(p)
            except Exception:
                pass
        deleted_count += 1

    db.resumes.delete_many({"user_id": current_user.id})
    return {"message": f"Successfully deleted {deleted_count} resumes and associated files"}

# ==============================================================================
# JOBS
# ==============================================================================
@router.get(
    "/jobs",
    response_model=List[JobRecord],
    summary="List all job descriptions submitted by the logged-in user",
)
def get_user_jobs(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    cursor = db.jobs.find({"user_id": current_user.id}).sort("created_at", -1)
    results = []
    for doc in cursor:
        results.append(JobRecord(
            id=str(doc["_id"]),
            user_id=doc.get("user_id", current_user.id),
            job_title=doc.get("job_title", "Target Role"),
            job_description=doc.get("job_description", ""),
            required_skills=doc.get("required_skills", []),
            preferred_skills=doc.get("preferred_skills", []),
            required_experience=doc.get("required_experience"),
            education_requirements=doc.get("education_requirements"),
            created_at=str(doc.get("created_at", "")),
        ))
    return results

@router.delete(
    "/jobs/{job_id}",
    summary="Delete a job record owned by the logged-in user",
)
def delete_user_job(
    job_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    query = {"_id": _to_object_id(job_id), "user_id": current_user.id}
    res = db.jobs.delete_one(query)
    if res.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description record not found or permission denied.",
        )
    return {"message": "Job description deleted successfully"}

@router.delete(
    "/jobs",
    summary="Permanently delete all job descriptions saved by the logged-in user",
)
def delete_all_user_jobs(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    res = db.jobs.delete_many({"user_id": current_user.id})
    return {"message": f"Successfully deleted {res.deleted_count} job descriptions"}

# ==============================================================================
# ANALYSES / MATCH HISTORY
# ==============================================================================
@router.get(
    "/analyses",
    response_model=List[AnalysisRecord],
    summary="List all previous match reports for the logged-in user",
)
def get_user_analyses(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    cursor = db.analyses.find({"user_id": current_user.id}).sort("created_at", -1)
    results = []
    for doc in cursor:
        results.append(AnalysisRecord(
            id=str(doc["_id"]),
            user_id=doc.get("user_id", current_user.id),
            resume_id=doc.get("resume_id"),
            job_id=doc.get("job_id"),
            resume_filename=doc.get("resume_filename", "Resume.pdf"),
            job_title=doc.get("job_title", "Target Role"),
            overall_match_percentage=doc.get("overall_match_percentage", 0),
            ats_score=doc.get("ats_score", 0),
            ats_grade=doc.get("ats_grade", "B"),
            matched_skills=doc.get("matched_skills", []),
            missing_skills=doc.get("missing_skills", []),
            summary_text=doc.get("summary_text"),
            report_data=doc.get("report_data"),
            created_at=str(doc.get("created_at", "")),
        ))
    return results

@router.get(
    "/analyses/{analysis_id}",
    response_model=AnalysisRecord,
    summary="Get a specific match report by ID to view full previous report",
)
def get_single_analysis(
    analysis_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    query = {"_id": _to_object_id(analysis_id), "user_id": current_user.id}
    doc = db.analyses.find_one(query)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match report not found or access denied.",
        )
    return AnalysisRecord(
        id=str(doc["_id"]),
        user_id=doc.get("user_id", current_user.id),
        resume_id=doc.get("resume_id"),
        job_id=doc.get("job_id"),
        resume_filename=doc.get("resume_filename", "Resume.pdf"),
        job_title=doc.get("job_title", "Target Role"),
        overall_match_percentage=doc.get("overall_match_percentage", 0),
        ats_score=doc.get("ats_score", 0),
        ats_grade=doc.get("ats_grade", "B"),
        matched_skills=doc.get("matched_skills", []),
        missing_skills=doc.get("missing_skills", []),
        summary_text=doc.get("summary_text"),
        report_data=doc.get("report_data"),
        created_at=str(doc.get("created_at", "")),
    )

@router.delete(
    "/analyses/{analysis_id}",
    summary="Delete a match report record owned by the logged-in user",
)
def delete_user_analysis(
    analysis_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    query = {"_id": _to_object_id(analysis_id), "user_id": current_user.id}
    res = db.analyses.delete_one(query)
    if res.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis report not found or permission denied.",
        )
    return {"message": "Match report record deleted successfully"}

@router.delete(
    "/analyses",
    summary="Permanently delete all match reports and analysis history for the logged-in user",
)
def delete_all_user_analyses(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    res = db.analyses.delete_many({"user_id": current_user.id})
    return {"message": f"Successfully cleared {res.deleted_count} analysis reports from history"}

@router.delete(
    "/account",
    summary="Step 18 Privacy: Permanently delete user account and all personal data",
    description="Purges user profile, uploaded resumes (and files), job descriptions, analysis reports, and comparisons.",
)
def delete_user_account(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    # 1. Purge all uploaded resume files
    cursor = db.resumes.find({"user_id": current_user.id})
    for doc in cursor:
        file_id = doc.get("file_id")
        if file_id:
            try:
                for p in settings.UPLOAD_DIR.glob(f"{file_id}_*"):
                    delete_file_permanently(p)
            except Exception:
                pass

    # 2. Delete database records
    db.resumes.delete_many({"user_id": current_user.id})
    db.jobs.delete_many({"user_id": current_user.id})
    db.analyses.delete_many({"user_id": current_user.id})
    if hasattr(db, "comparisons"):
        db.comparisons.delete_many({"user_id": current_user.id})
    db.users.delete_one({"_id": _to_object_id(current_user.id)})

    return {"message": "User account and all associated personal data permanently deleted"}

@router.post(
    "/analyses/save",
    response_model=AnalysisRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Save a match report to user's history",
)
def save_user_analysis(
    request: SaveAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    now_iso = datetime.now(timezone.utc).isoformat()
    doc = {
        "user_id": current_user.id,
        "resume_id": request.resume_id,
        "job_id": request.job_id,
        "resume_filename": request.resume_filename,
        "job_title": request.job_title,
        "overall_match_percentage": request.overall_match_percentage,
        "ats_score": request.ats_score or 0,
        "ats_grade": request.ats_grade or "B",
        "matched_skills": request.matched_skills or [],
        "missing_skills": request.missing_skills or [],
        "summary_text": request.summary_text,
        "report_data": request.report_data,
        "created_at": now_iso,
    }
    res = db.analyses.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return AnalysisRecord(**doc)

