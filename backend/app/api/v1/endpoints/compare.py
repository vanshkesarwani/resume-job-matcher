import logging
from typing import List, Any
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.mongodb import get_database
from app.schemas.auth import UserResponse
from app.schemas.comparison import (
    MultiJobCompareRequest,
    MultiJobCompareResponse,
)
from app.services.comparison_service import compare_multiple_jobs
from app.api.deps import get_optional_current_user, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

def _to_object_id(id_str: str) -> Any:
    return ObjectId(id_str) if ObjectId.is_valid(id_str) else id_str

@router.post(
    "/multi-jobs",
    response_model=MultiJobCompareResponse,
    summary="Compare a single resume against multiple job descriptions",
    description="Calculates match scores, skill overlaps, and ranks all jobs from highest to lowest match.",
)
def compare_multi_jobs_endpoint(
    request: MultiJobCompareRequest,
    current_user: UserResponse = Depends(get_optional_current_user),
    db=Depends(get_database),
):
    try:
        user_id = current_user.id if current_user else None
        response = compare_multiple_jobs(
            resume_text=request.resume_text,
            jobs=request.jobs,
            resume_filename=request.resume_filename or "Resume.pdf",
            user_id=user_id,
        )

        # If user is authenticated, persist the comparison session to history
        if current_user:
            try:
                doc = response.model_dump()
                doc["user_id"] = current_user.id
                res = db.comparisons.insert_one(doc)
                response.id = str(res.inserted_id)
            except Exception as e:
                logger.warning(f"Could not persist comparison session to database: {e}")

        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error during multi-job comparison: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-job comparison failed: {str(e)}",
        )

@router.get(
    "/history",
    response_model=List[MultiJobCompareResponse],
    summary="Get saved multi-job comparisons for the authenticated user",
)
def get_user_comparison_history(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    cursor = db.comparisons.find({"user_id": current_user.id}).sort("created_at", -1)
    results = []
    for doc in cursor:
        doc_id = str(doc.get("_id", ""))
        doc["id"] = doc_id
        results.append(MultiJobCompareResponse(**doc))
    return results

@router.delete(
    "/history/{comparison_id}",
    summary="Delete a saved multi-job comparison from history",
)
def delete_user_comparison(
    comparison_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database),
):
    query = {"_id": _to_object_id(comparison_id), "user_id": current_user.id}
    res = db.comparisons.delete_one(query)
    if res.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison record not found or permission denied.",
        )
    return {"message": "Comparison session deleted successfully"}

