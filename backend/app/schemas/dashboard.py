from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ExperienceMatchDetail(BaseModel):
    required_experience: str = Field(..., description="Required experience stated in job description")
    candidate_experience: str = Field(..., description="Estimated candidate experience extracted from resume")
    candidate_years: float = Field(default=0.0, description="Numerical estimate of candidate years")
    required_years: float = Field(default=0.0, description="Numerical estimate of required years")
    status: str = Field(..., description="e.g. Meets Requirement, Exceeds Requirement, Below Requirement, Flexible / Not Specified")
    score: int = Field(..., ge=0, le=100, description="Experience alignment score (0-100)")
    notes: str = Field(..., description="Human-friendly explanation of the experience evaluation")

class EducationMatchDetail(BaseModel):
    required_education: str = Field(..., description="Education requirements stated in job description")
    candidate_education: str = Field(..., description="Candidate degrees and academic credentials extracted from resume")
    highest_degree: str = Field(default="Not Specified", description="Candidate highest degree level found")
    status: str = Field(..., description="e.g. Meets Requirement, Exceeds Requirement, Equivalent Experience, Requirement Not Specified")
    score: int = Field(..., ge=0, le=100, description="Education alignment score (0-100)")
    notes: str = Field(..., description="Human-friendly explanation of the education evaluation")

class ATSCategoryItem(BaseModel):
    category: str = Field(..., description="e.g. Skills Coverage, Semantic Relevance, Experience, Education, ATS Hygiene")
    score: int = Field(..., ge=0, le=100)
    weight: str = Field(..., description="Weight in total score (e.g. 35%, 25%)")
    feedback: str = Field(..., description="Brief diagnostic on this category")

class ATSScoreBreakdown(BaseModel):
    overall_ats_score: int = Field(..., ge=0, le=100, description="Composite ATS readiness score (0-100)")
    grade: str = Field(..., description="e.g. A+, A, B, C, D")
    verdict: str = Field(..., description="e.g. High ATS Readiness, Moderate ATS Readiness, Needs Optimization")
    skills_score: int = Field(..., ge=0, le=100)
    semantic_score: int = Field(..., ge=0, le=100)
    experience_score: int = Field(..., ge=0, le=100)
    education_score: int = Field(..., ge=0, le=100)
    formatting_score: int = Field(..., ge=0, le=100)
    categories: List[ATSCategoryItem] = Field(default_factory=list)

class SummaryImprovement(BaseModel):
    current_summary: str = Field(default="", description="Original resume summary or notice that summary was missing")
    improved_summary: str = Field(..., description="Tailored executive summary matching target job description using only real facts")
    key_enhancements: List[str] = Field(default_factory=list, description="List of specific improvements applied")
    actionable_tips: str = Field(..., description="Practical advice for tailoring the summary")

class ProjectImprovement(BaseModel):
    project_name: str = Field(..., description="Name of candidate project")
    original_text: str = Field(default="", description="Original project bullet or description from resume")
    suggested_improvements: List[str] = Field(default_factory=list, description="Actionable recommendations to enhance project impact")
    recommended_action_verbs: List[str] = Field(default_factory=list, description="Action verbs to describe technical delivery")
    tech_stack_to_highlight: List[str] = Field(default_factory=list, description="Tools or technologies to explicitly call out")

class DashboardAnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=15, description="Full extracted resume text")
    job_description: str = Field(..., min_length=15, description="Target job description")
    resume_sections: Optional[Dict[str, Any]] = Field(default=None)
    required_skills: Optional[List[str]] = Field(default_factory=list)
    preferred_skills: Optional[List[str]] = Field(default_factory=list)
    job_title: Optional[str] = Field(default="")
    required_experience: Optional[str] = Field(default="")
    education_requirements: Optional[str] = Field(default="")

class DashboardAnalysisResponse(BaseModel):
    overall_match_percentage: int = Field(..., ge=0, le=100)
    ats_score: ATSScoreBreakdown
    experience_match: ExperienceMatchDetail
    education_match: EducationMatchDetail
    summary_improvement: SummaryImprovement
    project_improvements: List[ProjectImprovement] = Field(default_factory=list)
    matched_skills_count: int
    missing_skills_count: int
    verdict: str
    message: str = Field(default="Dashboard analysis completed successfully")

class PDFReportRequest(BaseModel):
    resume_filename: Optional[str] = Field(default="Candidate_Resume.pdf")
    job_title: Optional[str] = Field(default="Target Role")
    overall_match_percentage: int = Field(default=0)
    ats_score: Optional[Dict[str, Any]] = Field(default=None)
    skills_data: Optional[Dict[str, Any]] = Field(default=None)
    embedding_data: Optional[Dict[str, Any]] = Field(default=None)
    experience_match: Optional[Dict[str, Any]] = Field(default=None)
    education_match: Optional[Dict[str, Any]] = Field(default=None)
    llm_data: Optional[Dict[str, Any]] = Field(default=None)
    summary_improvement: Optional[Dict[str, Any]] = Field(default=None)
    project_improvements: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

