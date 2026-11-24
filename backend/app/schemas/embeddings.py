from pydantic import BaseModel, Field

class EmbeddingMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=15, description="Extracted resume text content")
    job_description: str = Field(..., min_length=15, description="Target job description text")

class EmbeddingMatchResponse(BaseModel):
    similarity_score: float = Field(..., description="Cosine similarity score between 0.0 and 1.0")
    similarity_percentage: float = Field(..., ge=0.0, le=100.0, description="Semantic similarity percentage (0-100%)")
    match_level: str = Field(..., description="e.g. High Semantic Alignment, Moderate Semantic Alignment, Low Semantic Alignment")
    embedding_dimension: int = Field(default=384, description="Vector dimension size of all-MiniLM-L6-v2")
    model_used: str = Field(default="all-MiniLM-L6-v2", description="Pre-trained sentence-transformers model")
    summary: str = Field(..., description="Beginner-friendly explanation of the semantic match")
    message: str = Field(default="Embeddings generated and cosine similarity calculated successfully", description="Status message")

