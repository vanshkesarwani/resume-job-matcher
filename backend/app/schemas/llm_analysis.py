from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BulletPointRewrite(BaseModel):
    """
    Rewritten resume bullet point using professional action verbs,
    strictly adhering to original candidate facts.
    """
    original: str = Field(..., description="Original bullet point text from candidate resume")
    improved: str = Field(..., description="Rewritten bullet point with strong action verbs and high recruiter impact")
    reasoning: str = Field(..., description="Why this rewrite improves ATS readability and impact")
    action_verb_used: str = Field(..., description="Primary action verb used (e.g., Engineered, Spearheaded, Accelerated)")

class SectionFeedback(BaseModel):
    """
    Audit diagnostic of an individual resume section.
    """
    section_name: str = Field(..., description="Name of the section (e.g. Work Experience, Skills, Summary, Projects, Education)")
    status: str = Field(..., description="Status: 'Strong', 'Needs Improvement', 'Weak', or 'Missing'")
    score_out_of_10: int = Field(..., ge=1, le=10, description="Quality score from 1 to 10")
    feedback: str = Field(..., description="Specific feedback on what is strong or deficient in this section")
    improvement_recommendation: str = Field(..., description="Actionable recommendation using existing resume facts only")

class KeywordSuggestion(BaseModel):
    """
    Relevant missing or under-emphasized keyword from the job description.
    """
    keyword: str = Field(..., description="Keyword or technical concept from the job description")
    category: str = Field(..., description="Category (e.g. 'Required Skill', 'Tool / Framework', 'Industry Concept')")
    context_advice: str = Field(..., description="Where and how to incorporate this accurately IF the user has actual experience")

class GeneralSuggestion(BaseModel):
    """
    Personalized resume improvement suggestion.
    """
    title: str = Field(..., description="Concise suggestion title")
    description: str = Field(..., description="Detailed personalized recommendation")
    priority: str = Field(..., description="Priority: 'High', 'Medium', or 'Low'")
    category: str = Field(..., description="Category (e.g. 'Action Verbs', 'ATS Formatting', 'Role Alignment', 'Quantification')")

class LLMAnalysisRequest(BaseModel):
    """
    Input payload for LLM resume analysis and improvement suggestions.
    """
    resume_text: str = Field(..., min_length=15, description="Full extracted text of the candidate resume")
    job_description: str = Field(..., min_length=15, description="Target job description posting")
    resume_sections: Optional[Dict[str, Any]] = Field(default=None, description="Optional structured resume sections (skills, experience, etc.)")
    job_title: Optional[str] = Field(default="", description="Target job title")
    missing_skills: Optional[List[str]] = Field(default_factory=list, description="Missing skills identified from matching")

class LLMAnalysisResponse(BaseModel):
    """
    Structured JSON output containing grounded resume improvements.
    """
    summary: str = Field(..., description="Executive summary of candidate fit and recommended improvements")
    overall_fit_assessment: str = Field(..., description="High-level qualitative fit against the job requirements")
    general_suggestions: List[GeneralSuggestion] = Field(default_factory=list, description="Personalized suggestions based strictly on resume data")
    bullet_rewrites: List[BulletPointRewrite] = Field(default_factory=list, description="Rewritten bullet points using professional action verbs")
    suggested_keywords: List[KeywordSuggestion] = Field(default_factory=list, description="Relevant missing keywords based on the job description")
    section_feedbacks: List[SectionFeedback] = Field(default_factory=list, description="Section-by-section audit identifying weak sections and fixes")
    provider_used: str = Field(..., description="LLM provider used (e.g. 'Google Gemini', 'OpenAI', 'Deterministic NLP Fallback')")
    model_name: str = Field(..., description="Model identifier used")
    grounding_guarantee: str = Field(
        default="Zero invented skills, projects, qualifications, or numbers. Suggestions strictly build upon your original resume.",
        description="Explicit guarantee regarding hallucination prevention"
    )
    message: str = Field(default="AI analysis and improvement suggestions generated successfully", description="Status message")

