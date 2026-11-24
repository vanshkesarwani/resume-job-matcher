from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ResumeRecord(BaseModel):
    id: str = Field(..., description="Resume record ID")
    user_id: str = Field(..., description="Owner user ID")
    filename: str = Field(..., description="Original uploaded filename")
    file_type: str = Field(..., description="pdf or docx")
    file_size: int = Field(..., description="File size in bytes")
    detected_skills: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = Field(default=None)
    created_at: str = Field(..., description="ISO creation timestamp")

class JobRecord(BaseModel):
    id: str = Field(..., description="Job record ID")
    user_id: str = Field(..., description="Owner user ID")
    job_title: str = Field(..., description="Extracted job title")
    job_description: str = Field(..., description="Raw job description text")
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    required_experience: Optional[str] = Field(default=None)
    education_requirements: Optional[str] = Field(default=None)
    created_at: str = Field(..., description="ISO creation timestamp")

class AnalysisRecord(BaseModel):
    id: str = Field(..., description="Analysis report ID")
    user_id: str = Field(..., description="Owner user ID")
    resume_id: Optional[str] = Field(default=None)
    job_id: Optional[str] = Field(default=None)
    resume_filename: str = Field(..., description="Filename of resume evaluated")
    job_title: str = Field(..., description="Target job title")
    overall_match_percentage: int = Field(..., ge=0, le=100)
    ats_score: int = Field(default=0, ge=0, le=100)
    ats_grade: str = Field(default="B")
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    summary_text: Optional[str] = Field(default=None)
    report_data: Optional[Dict[str, Any]] = Field(default=None, description="Full cached report object for instant reload")
    created_at: str = Field(..., description="ISO creation timestamp")

class SaveAnalysisRequest(BaseModel):
    resume_id: Optional[str] = None
    job_id: Optional[str] = None
    resume_filename: str = "Resume.pdf"
    job_title: str = "Target Role"
    overall_match_percentage: int = Field(..., ge=0, le=100)
    ats_score: Optional[int] = 0
    ats_grade: Optional[str] = "B"
    matched_skills: Optional[List[str]] = Field(default_factory=list)
    missing_skills: Optional[List[str]] = Field(default_factory=list)
    summary_text: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None

