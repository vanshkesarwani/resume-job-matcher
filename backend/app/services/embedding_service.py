import logging
from typing import Optional
from sentence_transformers import SentenceTransformer, util
from app.schemas.embeddings import EmbeddingMatchResponse

logger = logging.getLogger(__name__)

# Pre-trained model constant
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Singleton instance to ensure the model is loaded only once into memory
_model_instance: Optional[SentenceTransformer] = None

def get_embedding_model() -> SentenceTransformer:
    """
    Returns the loaded SentenceTransformer model instance.
    Loads 'all-MiniLM-L6-v2' on first call and caches it in memory.
    """
    global _model_instance
    if _model_instance is None:
        logger.info(f"Loading SentenceTransformer model '{MODEL_NAME}' into memory...")
        try:
            # Prefer local cached model files to avoid unnecessary network latency/retries
            _model_instance = SentenceTransformer(MODEL_NAME, local_files_only=True)
        except Exception:
            _model_instance = SentenceTransformer(MODEL_NAME)
        logger.info(f"Model '{MODEL_NAME}' loaded successfully.")
    return _model_instance

def compute_semantic_similarity(resume_text: str, job_description: str) -> EmbeddingMatchResponse:
    """
    Step 8: Embeddings & Cosine Similarity Comparison.
    
    1. Validates input texts.
    2. Converts resume text into a 384-dimensional numerical vector (embedding).
    3. Converts job description text into a 384-dimensional numerical vector.
    4. Computes cosine similarity between both vectors.
    5. Converts cosine similarity into a readable percentage (0-100%).
    6. Returns structured response with similarity score, percentage, and summary.
    """
    clean_resume = resume_text.strip()
    clean_jd = job_description.strip()

    if len(clean_resume) < 15:
        raise ValueError("Resume text is too brief for embedding generation. Minimum 15 characters required.")

    if len(clean_jd) < 15:
        raise ValueError("Job description is too brief for embedding generation. Minimum 15 characters required.")

    # 1. Load the pre-trained all-MiniLM-L6-v2 model
    model = get_embedding_model()

    # 2. Convert texts into numerical vectors (embeddings)
    resume_embedding = model.encode(clean_resume, convert_to_tensor=True)
    jd_embedding = model.encode(clean_jd, convert_to_tensor=True)

    # 3. Calculate Cosine Similarity
    raw_similarity = util.cos_sim(resume_embedding, jd_embedding).item()

    # 4. Clamp similarity score between 0.0 and 1.0
    clamped_similarity = max(0.0, min(1.0, float(raw_similarity)))
    similarity_percentage = round(clamped_similarity * 100, 2)

    # 5. Determine qualitative match level
    if similarity_percentage >= 80.0:
        match_level = "High Semantic Alignment"
        summary = (
            f"The resume and job description share strong contextual meaning ({similarity_percentage}%), "
            "indicating close alignment in overall role duties, technical domain, and project scope."
        )
    elif similarity_percentage >= 60.0:
        match_level = "Moderate Semantic Alignment"
        summary = (
            f"The resume has moderate contextual alignment ({similarity_percentage}%) with the job description. "
            "Key concepts overlap, but some specific responsibilities or domain requirements differ."
        )
    else:
        match_level = "Low Semantic Alignment"
        summary = (
            f"The resume has low contextual alignment ({similarity_percentage}%) with the target role. "
            "Tailoring work experience bullets and technical focus to better mirror the job description is recommended."
        )

    return EmbeddingMatchResponse(
        similarity_score=round(clamped_similarity, 4),
        similarity_percentage=similarity_percentage,
        match_level=match_level,
        embedding_dimension=EMBEDDING_DIMENSION,
        model_used=MODEL_NAME,
        summary=summary,
        message="Embeddings generated and cosine similarity calculated successfully",
    )

