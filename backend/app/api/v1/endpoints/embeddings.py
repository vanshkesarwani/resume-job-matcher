from fastapi import APIRouter, HTTPException
from app.schemas.embeddings import EmbeddingMatchRequest, EmbeddingMatchResponse
from app.services.embedding_service import compute_semantic_similarity

router = APIRouter()

@router.post(
    "/similarity",
    response_model=EmbeddingMatchResponse,
    summary="Compute semantic similarity between resume and job description using all-MiniLM-L6-v2 embeddings",
)
def get_embedding_similarity(request: EmbeddingMatchRequest):
    """
    Step 8: Embeddings & Semantic Similarity Endpoint.
    
    - Converts resume text into numerical embeddings using the 'all-MiniLM-L6-v2' model.
    - Converts job description text into numerical embeddings.
    - Computes Cosine Similarity between the vectors.
    - Returns similarity score (0.0 to 1.0) and similarity percentage (0% to 100%).
    """
    if not request.resume_text or not request.resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume text cannot be empty. Please provide valid resume text.",
        )

    if not request.job_description or not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty. Please provide valid job description text.",
        )

    try:
        response = compute_semantic_similarity(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while computing embeddings: {str(e)}",
        )

