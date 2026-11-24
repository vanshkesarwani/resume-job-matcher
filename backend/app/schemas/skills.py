from pydantic import BaseModel, Field
from typing import List, Optional

class SkillMatchRequest(BaseModel):
    resume_text: Optional[str] = Field(None, description="Extracted resume text")
    resume_skills: Optional[List[str]] = Field(default_factory=list, description="Explicit skills from resume")
    job_description: Optional[str] = Field(None, description="Raw job description text")
    required_skills: Optional[List[str]] = Field(default_factory=list, description="Required skills from JD")
    preferred_skills: Optional[List[str]] = Field(default_factory=list, description="Preferred/nice-to-have skills from JD")

class MatchedSkillDetail(BaseModel):
    skill: str = Field(..., description="Canonical skill name")
    type: str = Field(..., description="'required' or 'preferred'")
    synonym_match: bool = Field(default=False, description="Whether match was achieved via synonym mapping")
    matched_from: Optional[str] = Field(None, description="The original synonym variant found in the resume")

class MissingSkillDetail(BaseModel):
    skill: str = Field(..., description="Canonical skill name")
    type: str = Field(..., description="'required' or 'preferred'")
    importance: str = Field(..., description="'Mandatory' for required, 'Bonus' for preferred")

class SkillMatchResponse(BaseModel):
    overall_match_percentage: int = Field(..., ge=0, le=100, description="Weighted match score 0-100")
    required_match_percentage: int = Field(..., ge=0, le=100, description="Match score for required skills")
    preferred_match_percentage: int = Field(..., ge=0, le=100, description="Match score for preferred skills")
    verdict: str = Field(..., description="e.g. Strong Match, Moderate Match, Needs Optimization")
    matched_required: List[MatchedSkillDetail] = Field(default_factory=list)
    missing_required: List[MissingSkillDetail] = Field(default_factory=list)
    matched_preferred: List[MatchedSkillDetail] = Field(default_factory=list)
    missing_preferred: List[MissingSkillDetail] = Field(default_factory=list)
    additional_candidate_skills: List[str] = Field(default_factory=list, description="Candidate skills not in the JD")
    total_required_count: int
    total_preferred_count: int
    total_candidate_skills_count: int
    summary: str = Field(..., description="Actionable summary of the skill match results")

