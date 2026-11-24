import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.schemas.skills import SkillMatchRequest
from app.schemas.dashboard import (
    ExperienceMatchDetail,
    EducationMatchDetail,
    ATSCategoryItem,
    ATSScoreBreakdown,
    SummaryImprovement,
    ProjectImprovement,
    DashboardAnalysisResponse,
)
from app.services.skill_matcher_service import match_skills
from app.services.embedding_service import compute_semantic_similarity

DEGREE_HIERARCHY = {
    "phd": 5,
    "doctorate": 5,
    "master": 4,
    "ms": 4,
    "m.s.": 4,
    "mtech": 4,
    "m.tech": 4,
    "mba": 4,
    "bachelor": 3,
    "bs": 3,
    "b.s.": 3,
    "btech": 3,
    "b.tech": 3,
    "ba": 3,
    "b.a.": 3,
    "associate": 2,
    "diploma": 1,
}

def _parse_candidate_years_from_resume(text: str) -> float:
    """
    Extracts total years of experience from resume text.
    Looks for explicit statements like '3+ years', or calculates from date ranges (e.g. 2020 - 2024).
    """
    # 1. Check for explicit statement e.g. "5+ years of experience" or "3 years experience"
    exp_statement = re.search(r"(\d{1,2}(?:\.\d)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+relevant|\s+professional|\s+industry)?\s+experience", text, re.I)
    if exp_statement:
        try:
            return float(exp_statement.group(1))
        except ValueError:
            pass

    # 2. Parse date ranges e.g. "2020 - 2024", "2019 to Present", "Jan 2021 – Current"
    current_year = datetime.now().year
    year_ranges = re.findall(r"\b(20[0-2]\d|199\d)\s*(?:-|–|—|to)\s*(20[0-2]\d|present|current|now)\b", text, re.I)
    total_months = 0

    for start_str, end_str in year_ranges:
        try:
            start_yr = int(start_str)
            end_yr = current_year if end_str.lower() in ["present", "current", "now"] else int(end_str)
            if 0 <= (end_yr - start_yr) <= 30:
                total_months += (end_yr - start_yr) * 12
        except Exception:
            continue

    if total_months > 0:
        years = round(total_months / 12.0, 1)
        # Cap reasonable span if multiple overlapping roles
        return min(years, 20.0)

    # 3. Default conservative estimate based on length & depth
    if "experience" in text.lower():
        bullets = [line for line in text.splitlines() if len(line.strip()) > 30]
        if len(bullets) > 10:
            return 3.5
        elif len(bullets) > 5:
            return 2.0
    return 1.5

def _parse_required_years_from_jd(jd_text: str, explicit_req: Optional[str] = None) -> float:
    """Extract required years of experience from job description."""
    source_text = explicit_req if explicit_req and explicit_req.strip() else jd_text
    match = re.search(r"(\d{1,2}(?:\.\d)?)\+?\s*(?:to\s*(\d{1,2})\s*)?(?:years?|yrs?)", source_text, re.I)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return 0.0

def evaluate_experience_match(
    resume_text: str,
    job_description: str,
    explicit_req: Optional[str] = None,
) -> ExperienceMatchDetail:
    """Compares candidate experience years against JD requirement."""
    cand_years = _parse_candidate_years_from_resume(resume_text)
    req_years = _parse_required_years_from_jd(job_description, explicit_req)

    cand_str = f"{cand_years:g}+ years of professional experience"
    req_str = explicit_req if explicit_req and explicit_req.strip() else (f"{req_years:g}+ years" if req_years > 0 else "Not strictly specified")

    if req_years == 0:
        return ExperienceMatchDetail(
            required_experience=req_str,
            candidate_experience=cand_str,
            candidate_years=cand_years,
            required_years=0.0,
            status="Requirement Flexible",
            score=90,
            notes=f"The job posting does not mandate a strict minimum year count. Candidate possesses {cand_str}.",
        )

    if cand_years >= req_years:
        surplus = round(cand_years - req_years, 1)
        status = "Exceeds Requirement" if surplus >= 2 else "Meets Requirement"
        score = 100 if surplus >= 1 else 95
        notes = f"Candidate has {cand_str}, satisfying the target role's {req_str} requirement."
    elif cand_years >= (req_years * 0.7):
        status = "Near Requirement"
        score = 75
        notes = f"Candidate has {cand_str}, slightly below target {req_str}, but within viable hiring threshold."
    else:
        status = "Below Requirement"
        score = max(40, int((cand_years / req_years) * 80))
        notes = f"Candidate has {cand_str}, which falls short of the required {req_str}."

    return ExperienceMatchDetail(
        required_experience=req_str,
        candidate_experience=cand_str,
        candidate_years=cand_years,
        required_years=req_years,
        status=status,
        score=score,
        notes=notes,
    )

def _detect_highest_degree(text: str) -> Tuple[str, int]:
    """Detects highest academic credential in text and returns (degree_name, level_weight)."""
    text_lower = text.lower()
    highest_name = "Not Specified"
    highest_weight = 0

    patterns = [
        ("Ph.D. / Doctorate", ["phd", "ph.d", "doctorate", "doctoral"], 5),
        ("Master's Degree", ["master", "m.s.", "ms in", "mtech", "m.tech", "mba"], 4),
        ("Bachelor's Degree", ["bachelor", "b.s.", "bs in", "btech", "b.tech", "b.e.", "b.a.", "undergraduate"], 3),
        ("Associate's Degree", ["associate degree", "associate of", "a.s.", "a.a."], 2),
        ("Diploma / Certificate", ["diploma", "certification", "bootcamp"], 1),
    ]

    for name, keywords, weight in patterns:
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                if weight > highest_weight:
                    highest_weight = weight
                    highest_name = name

    return highest_name, highest_weight

def evaluate_education_match(
    resume_text: str,
    job_description: str,
    explicit_req: Optional[str] = None,
) -> EducationMatchDetail:
    """Compares candidate academic degrees against JD requirement."""
    cand_deg_name, cand_weight = _detect_highest_degree(resume_text)
    req_text = explicit_req if explicit_req and explicit_req.strip() else job_description
    req_deg_name, req_weight = _detect_highest_degree(req_text)

    # Extract snippets
    edu_match = re.search(r"(?:education|academic|degree)[\s\S]{0,250}", resume_text, re.I)
    cand_edu_snippet = cand_deg_name
    if edu_match:
        lines = [l.strip() for l in edu_match.group(0).splitlines() if len(l.strip()) > 10]
        if lines:
            cand_edu_snippet = f"{cand_deg_name} ({lines[0]})"

    req_str = explicit_req if explicit_req and explicit_req.strip() else (req_deg_name if req_weight > 0 else "Bachelor's degree or equivalent practical experience")

    if req_weight == 0:
        status = "Requirement Met"
        score = 90
        notes = f"Job has flexible education requirements. Candidate holds {cand_deg_name}."
    elif cand_weight >= req_weight:
        status = "Exceeds Requirement" if cand_weight > req_weight else "Meets Requirement"
        score = 100
        notes = f"Candidate's {cand_deg_name} satisfies the requested {req_str}."
    elif cand_weight == (req_weight - 1):
        status = "Equivalent Practical Experience"
        score = 80
        notes = f"Candidate has {cand_deg_name}; combined with industry experience this usually satisfies {req_str}."
    elif cand_weight > 0:
        status = "Partial Match"
        score = 65
        notes = f"Candidate holds {cand_deg_name}, whereas the posting emphasizes {req_str}."
    else:
        status = "Degree Not Explicitly Stated"
        score = 55
        notes = "No clear academic degree was detected on the resume. Highlighting educational background is advised."

    return EducationMatchDetail(
        required_education=req_str,
        candidate_education=cand_edu_snippet,
        highest_degree=cand_deg_name,
        status=status,
        score=score,
        notes=notes,
    )

def compute_comprehensive_ats_score(
    skills_score: int,
    semantic_score: int,
    experience_score: int,
    education_score: int,
    resume_text: str,
) -> ATSScoreBreakdown:
    """
    Computes weighted ATS readiness score with category diagnostics:
    - Skills Match: 35%
    - Semantic Meaning Fit: 25%
    - Experience Alignment: 20%
    - Education Match: 10%
    - ATS Formatting & Keyword Hygiene: 10%
    """
    # ATS formatting hygiene heuristics
    formatting_score = 90
    if len(resume_text) < 300:
        formatting_score -= 30
    if not re.search(r"\b(skills|technologies)\b", resume_text, re.I):
        formatting_score -= 20
    if not re.search(r"\b(experience|history|employment)\b", resume_text, re.I):
        formatting_score -= 20
    formatting_score = max(35, min(100, formatting_score))

    overall = int(round(
        skills_score * 0.35 +
        semantic_score * 0.25 +
        experience_score * 0.20 +
        education_score * 0.10 +
        formatting_score * 0.10
    ))
    overall = max(10, min(100, overall))

    if overall >= 90:
        grade = "A+"
        verdict = "Exceptional ATS Fit"
    elif overall >= 80:
        grade = "A"
        verdict = "Strong ATS Alignment"
    elif overall >= 70:
        grade = "B"
        verdict = "Good Candidate Fit"
    elif overall >= 60:
        grade = "C"
        verdict = "Moderate Alignment"
    else:
        grade = "D"
        verdict = "Needs Strategic Optimization"

    categories = [
        ATSCategoryItem(
            category="Technical Skills Match",
            score=skills_score,
            weight="35%",
            feedback="Direct overlap between job description mandatory skills and detected resume skills.",
        ),
        ATSCategoryItem(
            category="Semantic Role Relevance",
            score=semantic_score,
            weight="25%",
            feedback="Vector meaning alignment computed using all-MiniLM-L6-v2 embeddings.",
        ),
        ATSCategoryItem(
            category="Experience Depth",
            score=experience_score,
            weight="20%",
            feedback="Candidate professional tenure compared against job role seniority requirements.",
        ),
        ATSCategoryItem(
            category="Education & Credentials",
            score=education_score,
            weight="10%",
            feedback="Verification of required academic degree level and field of study.",
        ),
        ATSCategoryItem(
            category="ATS Keyword & Layout Hygiene",
            score=formatting_score,
            weight="10%",
            feedback="Standard section header detection, parser readability, and content density.",
        ),
    ]

    return ATSScoreBreakdown(
        overall_ats_score=overall,
        grade=grade,
        verdict=verdict,
        skills_score=skills_score,
        semantic_score=semantic_score,
        experience_score=experience_score,
        education_score=education_score,
        formatting_score=formatting_score,
        categories=categories,
    )

def generate_summary_improvement(
    resume_text: str,
    job_description: str,
    job_title: str,
    cand_years: float,
) -> SummaryImprovement:
    """Generates an improved professional summary grounded in the user's real experience."""
    summary_match = re.search(r"(?:summary|objective|profile|about me)[\s\:\-–]*\n([\s\S]{30,400}?)(?:\n\s*[A-Z][A-Za-z\s]{3,20}\:|\n\n|\Z)", resume_text, re.I)
    current_summary = summary_match.group(1).strip() if summary_match else ""

    # Detect candidate's top tools
    from app.services.parser_service import detect_skills_from_text
    cand_skills = detect_skills_from_text(resume_text)[:5]
    skills_phrase = ", ".join(cand_skills) if cand_skills else "modern software engineering practices"

    target_role = job_title if job_title and job_title.strip() else "Software Engineer"
    years_phrase = f"{cand_years:g}+ years of hands-on experience" if cand_years > 0 else "demonstrated background"

    improved_summary = (
        f"Accomplished {target_role} with {years_phrase} specializing in {skills_phrase}. "
        f"Proven track record of architecting scalable applications, collaborating cross-functionally, "
        f"and delivering high-reliability solutions tailored to target business objectives."
    )

    enhancements = [
        f"Aligned job title directly with target role: '{target_role}' to catch recruiter eye",
        f"Prominently featured primary skills ({skills_phrase}) in the first 25 words",
        "Replaced generic objective statements with active delivery and impact terminology",
    ]

    return SummaryImprovement(
        current_summary=current_summary if current_summary else "No formal summary section was detected on the resume.",
        improved_summary=improved_summary,
        key_enhancements=enhancements,
        actionable_tips="Place this summary at the very top of your resume right under your contact info to pass recruiter 6-second scans.",
    )

def generate_project_improvements(resume_text: str, job_description: str) -> List[ProjectImprovement]:
    """Generates targeted suggestions to enhance project descriptions using action verbs and structure."""
    # Find project section or bullet points with technical keywords
    project_blocks = re.findall(r"(?:project|portfolio|built|engineered)[\s\:\-–]*\n([\s\S]{30,300}?)(?:\n\n|\Z)", resume_text, re.I)
    results = []

    if project_blocks:
        for i, block in enumerate(project_blocks[:2]):
            first_line = block.strip().splitlines()[0]
            name = first_line[:40].strip(" :-*•")
            results.append(ProjectImprovement(
                project_name=name if name else f"Technical Project {i+1}",
                original_text=block.strip()[:200],
                suggested_improvements=[
                    "Frame the problem statement and business objective before describing the tech stack.",
                    "Explicitly state your individual architectural contributions and design decisions.",
                    "Include a live deployment link or GitHub repository URL if publicly accessible.",
                ],
                recommended_action_verbs=["Architected", "Engineered", "Implemented", "Containerized"],
                tech_stack_to_highlight=["FastAPI", "PostgreSQL", "Docker", "REST APIs"],
            ))

    if not results:
        results.append(ProjectImprovement(
            project_name="Featured Engineering Project",
            original_text="Full-stack / backend web application showcasing REST APIs and database design.",
            suggested_improvements=[
                "Create a dedicated 'Projects' section with 2-3 prominent portfolio items.",
                "Structure each project with: Project Name | Tech Stack | 2 Bullet Points of impact.",
                "Highlight real architectural challenges solved (e.g. database schema optimization, auth flow).",
            ],
            recommended_action_verbs=["Spearheaded", "Engineered", "Optimized", "Integrated"],
            tech_stack_to_highlight=["Python", "FastAPI", "PostgreSQL", "Git"],
        ))

    return results

def compute_full_dashboard_analysis(
    resume_text: str,
    job_description: str,
    resume_sections: Optional[Dict[str, Any]] = None,
    required_skills: Optional[List[str]] = None,
    preferred_skills: Optional[List[str]] = None,
    job_title: Optional[str] = "",
    required_experience: Optional[str] = "",
    education_requirements: Optional[str] = "",
) -> DashboardAnalysisResponse:
    """
    Step 11 & Step 12 Orchestrator:
    Combines skill matching, semantic embedding similarity, experience matching,
    education matching, ATS scoring, and AI summary/project improvement suggestions.
    """
    clean_resume = resume_text.strip()
    clean_jd = job_description.strip()

    # 1. Skill Match
    skill_request = SkillMatchRequest(
        resume_text=clean_resume,
        resume_skills=resume_sections.get("skills", []) if resume_sections else [],
        job_description=clean_jd,
        required_skills=required_skills or [],
        preferred_skills=preferred_skills or [],
    )
    skill_res = match_skills(skill_request)

    # 2. Semantic Embedding Similarity
    embed_res = compute_semantic_similarity(
        resume_text=clean_resume,
        job_description=clean_jd,
    )

    # 3. Experience Match
    exp_detail = evaluate_experience_match(
        resume_text=clean_resume,
        job_description=clean_jd,
        explicit_req=required_experience,
    )

    # 4. Education Match
    edu_detail = evaluate_education_match(
        resume_text=clean_resume,
        job_description=clean_jd,
        explicit_req=education_requirements,
    )

    # 5. Composite ATS Score
    ats_breakdown = compute_comprehensive_ats_score(
        skills_score=skill_res.overall_match_percentage,
        semantic_score=int(round(embed_res.similarity_percentage)),
        experience_score=exp_detail.score,
        education_score=edu_detail.score,
        resume_text=clean_resume,
    )

    # 6. Overall match percentage (average of skills, embeddings, and experience)
    overall_match = int(round(
        skill_res.overall_match_percentage * 0.40 +
        embed_res.similarity_percentage * 0.35 +
        exp_detail.score * 0.25
    ))
    overall_match = max(10, min(100, overall_match))

    # 7. Step 12 AI Suggestions: Summary & Projects
    cand_years = exp_detail.candidate_years
    summary_imp = generate_summary_improvement(
        resume_text=clean_resume,
        job_description=clean_jd,
        job_title=job_title or "",
        cand_years=cand_years,
    )
    project_imps = generate_project_improvements(clean_resume, clean_jd)

    return DashboardAnalysisResponse(
        overall_match_percentage=overall_match,
        ats_score=ats_breakdown,
        experience_match=exp_detail,
        education_match=edu_detail,
        summary_improvement=summary_imp,
        project_improvements=project_imps,
        matched_skills_count=len(skill_res.matched_required) + len(skill_res.matched_preferred),
        missing_skills_count=len(skill_res.missing_required) + len(skill_res.missing_preferred),
        verdict=ats_breakdown.verdict,
        message="Dashboard analysis, experience/education evaluation, and ATS scores computed successfully",
    )
