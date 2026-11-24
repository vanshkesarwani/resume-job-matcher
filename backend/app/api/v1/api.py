from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    resume,
    job,
    skills,
    embeddings,
    llm,
    dashboard,
    report,
    auth,
    user_data,
    analysis,
    compare,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Phase 5: Authentication"])
api_router.include_router(user_data.router, prefix="/user", tags=["Phase 5: User History & Records"])
api_router.include_router(compare.router, prefix="/compare", tags=["Phase 6: Multi-Job Comparison"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
api_router.include_router(job.router, prefix="/job", tags=["Job Description"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skill Matching"])
api_router.include_router(embeddings.router, prefix="/embeddings", tags=["Embeddings & Semantic Similarity"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM AI Analysis & Suggestions"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Phase 4: Dashboard Analysis"])
api_router.include_router(report.router, prefix="/report", tags=["Phase 4: PDF Report"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
