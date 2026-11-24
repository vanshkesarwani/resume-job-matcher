from pydantic import BaseModel, Field
from typing import List, Optional

class JobExtractRequest(BaseModel):
    job_description: str = Field(..., min_length=15, description="Raw job description text")

class JobExtractResponse(BaseModel):
    job_id: str = Field(..., description="Unique ID for this parsed job description")
    job_title: str = Field(..., description="Extracted or inferred job title")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory/required technical skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have or preferred skills")
    experience_required: str = Field(..., description="Required years of professional experience")
    education_requirements: List[str] = Field(default_factory=list, description="Extracted education/degree requirements")
    key_responsibilities: List[str] = Field(default_factory=list, description="List of primary job responsibilities and duties")
    raw_text: str = Field(..., description="Original job description text")
    extracted_at: str = Field(..., description="Timestamp of analysis")
    message: str = Field(default="Job description parsed and extracted successfully", description="Status message")

