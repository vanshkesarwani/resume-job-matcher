from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ResumeSections(BaseModel):
    professional_summary: Optional[str] = Field(default="", description="Extracted professional summary or objective")
    skills: List[str] = Field(default_factory=list, description="Extracted skills and competencies")
    work_experience: List[str] = Field(default_factory=list, description="Extracted work history entries")
    education: List[str] = Field(default_factory=list, description="Extracted education details")
    projects: List[str] = Field(default_factory=list, description="Extracted projects and achievements")
    raw_sections: Dict[str, str] = Field(default_factory=dict, description="Raw text of each detected section")

class ResumeUploadResponse(BaseModel):
    file_id: str = Field(..., description="Unique secure identifier for the stored resume")
    filename: str = Field(..., description="Original filename of the uploaded resume")
    file_size_bytes: int = Field(..., description="Size of file in bytes")
    extracted_text_length: int = Field(..., description="Total characters extracted")
    detected_skills: List[str] = Field(default_factory=list, description="Extracted core competencies")
    sections: ResumeSections = Field(..., description="Structured sections of the resume")
    raw_text: Optional[str] = Field(None, description="Extracted raw text content")
    message: str = Field(default="Resume uploaded and processed successfully", description="Status message")
