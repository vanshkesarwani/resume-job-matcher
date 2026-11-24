from pydantic import BaseModel, Field
from typing import List

class MatchAnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Extracted text from resume")
    job_description: str = Field(..., min_length=10, description="Target job description posting")

class CategoryScore(BaseModel):
    name: str
    percentage: int

class SuggestionItem(BaseModel):
    impact: str = Field(..., description="High Impact | Medium Impact | Formatting Check")
    title: str
    description: str

class MatchAnalysisResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="ATS match score from 0 to 100")
    match_level: str = Field(..., description="e.g. Strong Match, Moderate Match, Needs Optimization")
    total_matched: int
    total_missing: int
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    category_breakdown: List[CategoryScore] = Field(default_factory=list)
    suggestions: List[SuggestionItem] = Field(default_factory=list)

