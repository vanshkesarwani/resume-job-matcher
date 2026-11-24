from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SingleJobInput(BaseModel):
    job_id: Optional[str] = Field(default=None, description="Optional unique identifier for the job")
    job_title: str = Field(default="Target Role", min_length=2, max_length=100, description="Job title")
    company: Optional[str] = Field(default="Company", max_length=100, description="Hiring company name")
    job_description: str = Field(..., min_length=15, description="Full job description text")
    required_skills: Optional[List[str]] = Field(default_factory=list, description="Explicitly specified required skills")
    preferred_skills: Optional[List[str]] = Field(default_factory=list, description="Explicitly specified preferred skills")
    required_experience: Optional[str] = Field(default=None, description="e.g. '3+ years'")
    education_requirements: Optional[str] = Field(default=None, description="e.g. 'Bachelor in Computer Science'")

class MultiJobCompareRequest(BaseModel):
    resume_text: str = Field(..., min_length=15, description="Candidate's raw resume text")
    resume_filename: Optional[str] = Field(default="Resume.pdf", description="Original resume filename")
    jobs: List[SingleJobInput] = Field(..., min_length=2, max_length=10, description="List of 2 to 10 job descriptions to compare against")

class JobMatchComparisonItem(BaseModel):
    job_id: str = Field(..., description="Job identifier")
    job_title: str = Field(..., description="Job Title")
    company: Optional[str] = Field(default="Company", description="Company Name")
    rank: int = Field(..., ge=1, description="Rank from 1 (best match) to N")
    match_score: int = Field(..., ge=0, le=100, description="Overall match percentage (0-100%)")
    ats_score: int = Field(..., ge=0, le=100, description="Comprehensive ATS readiness score")
    ats_grade: str = Field(default="B", description="A+, A, B, C, or D")
    semantic_similarity: float = Field(..., ge=0.0, le=100.0, description="Embedding cosine similarity percentage")
    skills_score: int = Field(..., ge=0, le=100, description="Skills overlap score")
    matched_skills: List[str] = Field(default_factory=list, description="List of skills possessed by candidate matching this job")
    missing_skills: List[str] = Field(default_factory=list, description="List of skills required by this job but missing in resume")
    matched_skills_count: int = Field(default=0)
    missing_skills_count: int = Field(default=0)
    experience_status: str = Field(default="Meets Requirement")
    education_status: str = Field(default="Requirement Met")
    summary: str = Field(..., description="Short diagnostic summary for this specific match")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths for this role")
    key_recommendation: str = Field(..., description="Actionable tip to increase chances for this job")
    full_report: Optional[Dict[str, Any]] = Field(default=None, description="Cached full dashboard report for one-click in-depth view")

class MultiJobCompareResponse(BaseModel):
    id: Optional[str] = Field(default=None, description="Database record ID if saved")
    user_id: Optional[str] = Field(default=None, description="User ID if authenticated")
    resume_filename: str = Field(default="Resume.pdf")
    total_jobs_compared: int = Field(..., ge=2)
    top_recommended_job: Optional[JobMatchComparisonItem] = Field(default=None, description="Rank #1 best match")
    ranked_jobs: List[JobMatchComparisonItem] = Field(..., description="All compared jobs ordered from highest to lowest match score")
    comparison_summary: str = Field(..., description="Comparative insight summarizing ranking and skill trends")
    created_at: str = Field(..., description="ISO creation timestamp")

