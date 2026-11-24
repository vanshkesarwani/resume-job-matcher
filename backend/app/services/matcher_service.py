import re
from typing import List, Tuple
from app.schemas.analysis import MatchAnalysisResponse, CategoryScore, SuggestionItem
from app.services.parser_service import detect_skills_from_text

def analyze_resume_against_job(resume_text: str, job_description: str) -> MatchAnalysisResponse:
    """Compare resume text against a job description, compute ATS score and suggestions."""
    # 1. Detect skills in both texts
    jd_skills = detect_skills_from_text(job_description)
    resume_skills = detect_skills_from_text(resume_text)

    # If JD didn't match standard skills, extract general frequent keywords (length >= 4)
    if not jd_skills:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", job_description.lower())
        jd_skills = sorted(list(set(words[:10])))

    # 2. Identify matched vs missing
    matched = [s for s in jd_skills if s.lower() in [r.lower() for r in resume_skills]]
    missing = [s for s in jd_skills if s.lower() not in [r.lower() for r in resume_skills]]

    # 3. Calculate Scores
    total_reqs = len(jd_skills) if jd_skills else 1
    skill_coverage = len(matched) / total_reqs

    # Word frequency overlap score
    jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower()))
    resume_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", resume_text.lower()))
    word_overlap = len(jd_words.intersection(resume_words)) / max(len(jd_words), 1)

    # Category breakdowns
    tech_score = int(min(100, max(20, skill_coverage * 100)))
    exp_score = int(min(100, max(30, (skill_coverage * 0.6 + word_overlap * 0.4) * 100)))
    ats_formatting_score = 90 if len(resume_text) > 200 else 60
    keyword_density_score = int(min(100, max(25, word_overlap * 120)))

    # Overall weighted score
    overall = int(round(
        tech_score * 0.40 +
        exp_score * 0.30 +
        ats_formatting_score * 0.15 +
        keyword_density_score * 0.15
    ))
    overall = min(100, max(15, overall))

    # Match Level classification
    if overall >= 80:
        match_level = "Strong Match"
    elif overall >= 60:
        match_level = "Moderate Match"
    else:
        match_level = "Needs Optimization"

    category_breakdown = [
        CategoryScore(name="Technical Skills Match", percentage=tech_score),
        CategoryScore(name="Experience Relevance", percentage=exp_score),
        CategoryScore(name="Formatting & ATS Readability", percentage=ats_formatting_score),
        CategoryScore(name="Keywords Density", percentage=keyword_density_score),
    ]

    # Generate targeted suggestions
    suggestions: List[SuggestionItem] = []

    if missing:
        top_missing = ", ".join(missing[:4])
        suggestions.append(
            SuggestionItem(
                impact="High Impact",
                title=f"Incorporate Missing Target Keywords",
                description=f"The job posting explicitly values: {top_missing}. Add relevant projects or experience demonstrating these competencies.",
            )
        )

    suggestions.append(
        SuggestionItem(
            impact="Medium Impact",
            title="Quantify Project Outcomes",
            description="Use concrete metrics (percentages, speedups, or scale) in work bullet points to highlight business impact.",
        )
    )

    if overall < 75:
        suggestions.append(
            SuggestionItem(
                impact="Formatting Check",
                title="Align Section Headers",
                description="Ensure clear standard section headers (Summary, Experience, Skills, Education) so automated applicant tracking parsers index your data accurately.",
            )
        )

    return MatchAnalysisResponse(
        overall_score=overall,
        match_level=match_level,
        total_matched=len(matched),
        total_missing=len(missing),
        matched_skills=matched,
        missing_skills=missing,
        category_breakdown=category_breakdown,
        suggestions=suggestions,
    )

