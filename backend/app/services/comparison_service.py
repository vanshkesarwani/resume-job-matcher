import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import Counter

from app.schemas.skills import SkillMatchRequest
from app.schemas.comparison import (
    SingleJobInput,
    JobMatchComparisonItem,
    MultiJobCompareResponse,
)
from app.services.skill_matcher_service import match_skills
from app.services.embedding_service import compute_semantic_similarity
from app.services.dashboard_service import (
    evaluate_experience_match,
    evaluate_education_match,
    compute_comprehensive_ats_score,
    generate_summary_improvement,
    generate_project_improvements,
)

logger = logging.getLogger(__name__)

def compare_multiple_jobs(
    resume_text: str,
    jobs: List[SingleJobInput],
    resume_filename: str = "Resume.pdf",
    user_id: Optional[str] = None,
) -> MultiJobCompareResponse:
    """
    Step 16: Multiple Job Comparison Service.
    
    1. Validates input resume and at least 2 job descriptions.
    2. Compares the resume against each job description using:
       - Skill Matching (Required & Preferred, canonical synonym resolution)
       - Semantic Embedding Similarity (all-MiniLM-L6-v2 cosine similarity)
       - Experience Tenure Evaluation
       - Education Credential Matching
       - Weighted ATS Readiness Score
    3. Ranks all jobs from highest to lowest match score.
    4. Identifies cross-job skill trends and common gaps.
    5. Returns structured comparison response with top recommendation.
    """
    clean_resume = resume_text.strip()
    if len(clean_resume) < 15:
        raise ValueError("Resume text is too brief for multi-job comparison. Minimum 15 characters required.")

    if not jobs or len(jobs) < 2:
        raise ValueError("At least 2 job descriptions are required for comparison.")

    evaluated_items: List[Dict[str, Any]] = []
    all_missing_skills: List[str] = []

    for idx, job in enumerate(jobs):
        job_id = job.job_id or f"job_{idx + 1}"
        clean_jd = job.job_description.strip()
        title = job.job_title.strip() if job.job_title else f"Role #{idx + 1}"
        company = job.company.strip() if job.company else "Company"

        # 1. Skill Match
        skill_req = SkillMatchRequest(
            resume_text=clean_resume,
            job_description=clean_jd,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
        )
        skill_res = match_skills(skill_req)

        # 2. Semantic Similarity
        embed_res = compute_semantic_similarity(
            resume_text=clean_resume,
            job_description=clean_jd,
        )

        # 3. Experience Match
        exp_detail = evaluate_experience_match(
            resume_text=clean_resume,
            job_description=clean_jd,
            explicit_req=job.required_experience,
        )

        # 4. Education Match
        edu_detail = evaluate_education_match(
            resume_text=clean_resume,
            job_description=clean_jd,
            explicit_req=job.education_requirements,
        )

        # 5. ATS Score
        ats_breakdown = compute_comprehensive_ats_score(
            skills_score=skill_res.overall_match_percentage,
            semantic_score=int(round(embed_res.similarity_percentage)),
            experience_score=exp_detail.score,
            education_score=edu_detail.score,
            resume_text=clean_resume,
        )

        # 6. Overall Match Score (weighted composite)
        match_score = int(round(
            skill_res.overall_match_percentage * 0.40 +
            embed_res.similarity_percentage * 0.35 +
            exp_detail.score * 0.25
        ))
        match_score = max(10, min(100, match_score))

        # Skill lists
        matched_skills_list = [m.skill for m in skill_res.matched_required] + [
            m.skill for m in skill_res.matched_preferred
        ]
        # Deduplicate preserving order
        seen_matched = set()
        matched_skills = []
        for s in matched_skills_list:
            if s.lower() not in seen_matched:
                seen_matched.add(s.lower())
                matched_skills.append(s)

        missing_skills_list = [m.skill for m in skill_res.missing_required] + [
            m.skill for m in skill_res.missing_preferred
        ]
        seen_missing = set()
        missing_skills = []
        for s in missing_skills_list:
            if s.lower() not in seen_missing:
                seen_missing.add(s.lower())
                missing_skills.append(s)
                all_missing_skills.append(s)

        # Key strengths
        strengths = []
        if matched_skills:
            strengths.append(f"Strong overlap in core tools: {', '.join(matched_skills[:3])}")
        if exp_detail.score >= 80:
            strengths.append(f"{exp_detail.status} ({exp_detail.candidate_experience})")
        if embed_res.similarity_percentage >= 70:
            strengths.append(f"High contextual domain alignment ({embed_res.similarity_percentage}%)")

        if not strengths:
            strengths.append("Foundational technical background compatible with entry-to-mid requirements")

        # Recommendation
        if missing_skills:
            key_recommendation = (
                f"Bridge high-priority gaps in {', '.join(missing_skills[:2])} to significantly boost match readiness."
            )
        else:
            key_recommendation = "Excellent alignment! Emphasize measurable production outcomes in your interview."

        # Diagnostic summary
        summary = (
            f"Achieves a {match_score}% match score with {ats_breakdown.grade} ATS readiness. "
            f"Possesses {len(matched_skills)} matching skills and {len(missing_skills)} missing keywords."
        )

        # Full cached report for instant deep-dive loading
        full_report = {
            "overall_match_percentage": match_score,
            "ats_score": ats_breakdown.model_dump(),
            "experience_match": exp_detail.model_dump(),
            "education_match": edu_detail.model_dump(),
            "skill_match": skill_res.model_dump(),
            "semantic_match": embed_res.model_dump(),
            "summary_improvement": generate_summary_improvement(
                clean_resume, clean_jd, title, exp_detail.candidate_years
            ).model_dump(),
            "project_improvements": [
                pi.model_dump() for pi in generate_project_improvements(clean_resume, clean_jd)
            ],
            "matched_skills_count": len(matched_skills),
            "missing_skills_count": len(missing_skills),
            "verdict": ats_breakdown.verdict,
            "target_job_title": title,
            "target_company": company,
            "job_description_raw": clean_jd,
        }

        evaluated_items.append({
            "job_id": job_id,
            "job_title": title,
            "company": company,
            "match_score": match_score,
            "ats_score": ats_breakdown.overall_ats_score,
            "ats_grade": ats_breakdown.grade,
            "semantic_similarity": embed_res.similarity_percentage,
            "skills_score": skill_res.overall_match_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_skills_count": len(matched_skills),
            "missing_skills_count": len(missing_skills),
            "experience_status": exp_detail.status,
            "education_status": edu_detail.status,
            "summary": summary,
            "strengths": strengths,
            "key_recommendation": key_recommendation,
            "full_report": full_report,
        })

    # Rank jobs: sort descending by match_score, then ats_score, then skills_score
    evaluated_items.sort(
        key=lambda item: (item["match_score"], item["ats_score"], item["skills_score"]),
        reverse=True,
    )

    ranked_jobs: List[JobMatchComparisonItem] = []
    for rank_idx, item in enumerate(evaluated_items, start=1):
        item["rank"] = rank_idx
        ranked_jobs.append(JobMatchComparisonItem(**item))

    top_recommended = ranked_jobs[0] if ranked_jobs else None

    # Cross-role insight generation
    top_title = top_recommended.job_title if top_recommended else "None"
    top_score = top_recommended.match_score if top_recommended else 0
    lowest_score = ranked_jobs[-1].match_score if ranked_jobs else 0
    spread = top_score - lowest_score

    # Find common missing skills across multiple jobs
    skill_counts = Counter(all_missing_skills)
    frequent_gaps = [skill for skill, cnt in skill_counts.most_common(3) if cnt >= 2]

    if frequent_gaps:
        gap_insight = f"Skills frequently missing across multiple target roles include: {', '.join(frequent_gaps)}."
    else:
        gap_insight = "Each role has specialized requirements without overlapping skill deficits."

    comparison_summary = (
        f"Compared {len(jobs)} job descriptions against {resume_filename}. "
        f"'{top_title}' is your top recommendation with a {top_score}% match score "
        f"({spread}% higher than the lowest match at {lowest_score}%). {gap_insight}"
    )

    now_iso = datetime.now(timezone.utc).isoformat()

    return MultiJobCompareResponse(
        resume_filename=resume_filename,
        total_jobs_compared=len(ranked_jobs),
        top_recommended_job=top_recommended,
        ranked_jobs=ranked_jobs,
        comparison_summary=comparison_summary,
        created_at=now_iso,
        user_id=user_id,
    )
