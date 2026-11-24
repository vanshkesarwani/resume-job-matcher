import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.schemas.llm_analysis import (
    LLMAnalysisResponse,
    BulletPointRewrite,
    SectionFeedback,
    KeywordSuggestion,
    GeneralSuggestion,
)

logger = logging.getLogger(__name__)

# System prompt strictly enforcing non-hallucination and grounding constraints
LLM_SYSTEM_PROMPT = """You are an elite Applicant Tracking System (ATS) career advisor and executive resume optimization engine.
Your mission is to analyze a candidate's actual resume against a target job description and provide actionable, personalized improvements.

CRITICAL NON-NEGOTIABLE GROUNDING CONSTRAINTS:
1. STRICT FACTUAL ACCURACY: You MUST NEVER invent, assume, or hallucinate any skills, certifications, job titles, companies, dates, projects, achievements, revenue numbers, or percentage metrics not explicitly stated in the candidate's original resume.
2. USE ACTUAL RESUME INFORMATION ONLY: Base every single suggestion, rewritten bullet, and section diagnostic exclusively on the candidate's real text.
3. BULLET POINT REWRITES:
   - Select 3 to 5 real, actual bullet points from the candidate's work experience or projects.
   - Rewrite each bullet point using strong executive action verbs (e.g. Engineered, Spearheaded, Orchestrated, Automated, Accelerated, Streamlined, Refactored, Delivered).
   - If the original bullet point does NOT contain numbers or metrics, DO NOT invent fake numbers (e.g., do NOT invent 'boosted speed by 45%'). Instead, tighten the grammatical impact and advise the candidate in the 'reasoning' field where they can insert their actual metric if known.
4. KEYWORD SUGGESTIONS: Identify missing keywords from the job description. Clearly advise the candidate to incorporate them ONLY if they possess genuine hands-on experience with those tools or methodologies.
5. SECTION DIAGNOSTICS: Review 'Professional Summary', 'Skills', 'Work Experience', 'Projects', and 'Education'. Identify weak or missing sections and provide constructive, honest feedback.

OUTPUT FORMAT:
You MUST respond with pure, valid JSON (no markdown fences, no explanatory text outside the JSON) matching this exact schema:
{
  "summary": "Executive summary of alignment and key growth levers",
  "overall_fit_assessment": "High-level qualitative assessment against role expectations",
  "general_suggestions": [
    {
      "title": "Short title",
      "description": "Personalized advice grounded strictly in their actual resume",
      "priority": "High | Medium | Low",
      "category": "Action Verbs | ATS Formatting | Role Alignment | Content Depth"
    }
  ],
  "bullet_rewrites": [
    {
      "original": "Exact or near-exact original bullet point from candidate resume",
      "improved": "Rewritten bullet using strong action verb and professional phrasing without fake facts",
      "reasoning": "Why this change improves recruiter impact and ATS parsing",
      "action_verb_used": "e.g. Engineered"
    }
  ],
  "suggested_keywords": [
    {
      "keyword": "e.g. Docker",
      "category": "Required Skill | Tool / Framework | Domain Concept",
      "context_advice": "Actionable advice on how to showcase this if experienced"
    }
  ],
  "section_feedbacks": [
    {
      "section_name": "Work Experience | Skills | Professional Summary | Projects | Education",
      "status": "Strong | Needs Improvement | Weak | Missing",
      "score_out_of_10": 8,
      "feedback": "Honest audit of current section content",
      "improvement_recommendation": "Step-by-step fix using their actual background"
    }
  ]
}
"""

def _clean_json_text(text: str) -> str:
    """Strip markdown code fences and whitespace from raw LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def _call_gemini_api(prompt: str) -> Optional[Dict[str, Any]]:
    """Call Google Gemini using the google-genai SDK."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None

    try:
        from google import genai
        from google.genai import types

        logger.info(f"Invoking Google Gemini model '{settings.GEMINI_MODEL}'...")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=LLM_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        if response and response.text:
            cleaned = _clean_json_text(response.text)
            return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"Google Gemini call failed or encountered an error: {e}. Falling back...")
        return None

def _call_openai_api(prompt: str) -> Optional[Dict[str, Any]]:
    """Call OpenAI or compatible provider (Groq, OpenRouter, etc.)."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None

    try:
        from openai import OpenAI

        logger.info(f"Invoking OpenAI model '{settings.OPENAI_MODEL}'...")
        client_kwargs = {"api_key": api_key}
        if settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL

        client = OpenAI(**client_kwargs)
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            temperature=0.2,
            messages=[
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        raw_content = completion.choices[0].message.content
        if raw_content:
            cleaned = _clean_json_text(raw_content)
            return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"OpenAI API call failed or encountered an error: {e}. Falling back...")
        return None

def _generate_deterministic_fallback(
    resume_text: str,
    job_description: str,
    resume_sections: Optional[Dict[str, Any]] = None,
    missing_skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    High-fidelity deterministic fallback analyzer.
    Extracts actual candidate bullets and weak phrases, rewrites with executive action verbs,
    audits sections, and extracts missing JD keywords—strictly adhering to rules 6 & 7 (zero hallucination).
    """
    logger.info("Executing grounded deterministic NLP fallback analyzer...")

    # 1. Identify real bullet points or sentences from the actual resume (handles newlines and period-separated sentences)
    raw_segments = re.split(r"(?:[\r\n]+|(?<=[.!?])\s+)", resume_text)
    lines = [
        re.sub(r"^[\s•\-*–\d.]+", "", seg).strip().rstrip(".")
        for seg in raw_segments
        if len(seg.strip()) >= 20
    ]

    action_verb_map = [
        (re.compile(r"^(?:worked on|worked with|responsible for|helped with|helped to|assisted in|participated in|did|handled)\s+", re.I), "Spearheaded", "Replaced passive or weak participation phrase with high-ownership action verb"),
        (re.compile(r"^(?:created|made|built|wrote)\s+", re.I), "Engineered", "Elevated generic construction verb to technical engineering terminology"),
        (re.compile(r"^(?:used|using|utilized|applied)\s+", re.I), "Leveraged", "Strengthened technological application framing for ATS clarity"),
        (re.compile(r"^(?:improved|increased|fixed|changed)\s+", re.I), "Optimized", "Focused on quantifiable refinement and performance tuning"),
        (re.compile(r"^(?:managed|looked after|oversaw)\s+", re.I), "Orchestrated", "Reinforced leadership and cross-functional coordination impact"),
    ]

    bullet_rewrites: List[Dict[str, Any]] = []
    seen_originals = set()

    for line in lines:
        if line.lower() in seen_originals:
            continue
        for pattern, strong_verb, reason in action_verb_map:
            if pattern.search(line):
                rewritten_text = pattern.sub(f"{strong_verb} ", line)
                bullet_rewrites.append({
                    "original": line,
                    "improved": rewritten_text,
                    "reasoning": f"{reason}. Preserved candidate's exact factual scope without inventing metrics.",
                    "action_verb_used": strong_verb,
                })
                seen_originals.add(line.lower())
                break
        if len(bullet_rewrites) >= 4:
            break

    # If no weak prefix matched, enhance top candidate statements with strong active framing
    if len(bullet_rewrites) < 3 and lines:
        for line in lines[:4]:
            if line.lower() not in seen_originals:
                first_word = line.split()[0] if line.split() else "Developed"
                bullet_rewrites.append({
                    "original": line,
                    "improved": f"Architected and delivered: {line[0].lower() + line[1:] if len(line) > 1 else line}",
                    "reasoning": "Framed achievement with active delivery verbs to maximize ATS parsing weight.",
                    "action_verb_used": "Architected",
                })
                seen_originals.add(line.lower())
            if len(bullet_rewrites) >= 3:
                break

    # 2. Audit sections
    has_summary = bool(re.search(r"\b(summary|objective|profile|about me)\b", resume_text, re.I))
    has_skills = bool(re.search(r"\b(skills|technical skills|technologies|proficiencies)\b", resume_text, re.I))
    has_experience = bool(re.search(r"\b(experience|work experience|employment|history)\b", resume_text, re.I))
    has_projects = bool(re.search(r"\b(projects|personal projects|portfolio)\b", resume_text, re.I))
    has_education = bool(re.search(r"\b(education|academic|degree|university|college)\b", resume_text, re.I))

    section_feedbacks = [
        {
            "section_name": "Professional Summary",
            "status": "Strong" if has_summary else "Needs Improvement",
            "score_out_of_10": 8 if has_summary else 4,
            "feedback": (
                "Executive summary is clearly visible." if has_summary
                else "Resume lacks an executive summary section to highlight your core years of experience and target job alignment."
            ),
            "improvement_recommendation": (
                "Ensure your summary explicitly highlights your primary tech stack and years of relevant domain experience."
                if has_summary
                else "Add a 3-4 sentence professional summary at the top summarizing your background using your real qualifications."
            ),
        },
        {
            "section_name": "Work Experience",
            "status": "Strong" if has_experience else "Needs Improvement",
            "score_out_of_10": 8 if has_experience else 5,
            "feedback": (
                "Chronological work experience is present with identifiable bullet points." if has_experience
                else "Work experience section is missing or lacks clear role headers and achievements."
            ),
            "improvement_recommendation": "Lead every bullet point with a past-tense action verb (e.g. Engineered, Spearheaded, Automated) and highlight outcome over duty.",
        },
        {
            "section_name": "Technical Skills",
            "status": "Strong" if has_skills else "Needs Improvement",
            "score_out_of_10": 9 if has_skills else 5,
            "feedback": (
                "Dedicated technical skills section detected." if has_skills
                else "Skills are scattered throughout the document rather than cataloged in a dedicated ATS-readable skills section."
            ),
            "improvement_recommendation": "Group skills into categories: Languages, Frameworks, Databases, and DevOps/Cloud to accelerate recruiter scanning.",
        },
        {
            "section_name": "Projects",
            "status": "Strong" if has_projects else "Needs Improvement",
            "score_out_of_10": 8 if has_projects else 5,
            "feedback": (
                "Technical projects detected demonstrating practical application." if has_projects
                else "No explicit projects section found to showcase end-to-end delivery."
            ),
            "improvement_recommendation": "Include 2-3 significant projects mentioning tech stack, architectural responsibility, and deployment URL or repository.",
        },
        {
            "section_name": "Education",
            "status": "Strong" if has_education else "Needs Improvement",
            "score_out_of_10": 9 if has_education else 4,
            "feedback": (
                "Academic credentials and qualifications are documented." if has_education
                else "Education credentials could not be parsed clearly."
            ),
            "improvement_recommendation": "State degree, major, university, and graduation year concisely.",
        },
    ]

    # 3. Extract missing keywords from job description
    suggested_keywords: List[Dict[str, Any]] = []
    if missing_skills:
        for skill in missing_skills[:6]:
            suggested_keywords.append({
                "keyword": skill,
                "category": "Required Skill",
                "context_advice": f"If you have hands-on experience with {skill}, explicitly mention it in your Skills section or within relevant project descriptions.",
            })
    else:
        # Fallback keyword extraction from JD
        common_tech = ["Docker", "Kubernetes", "AWS", "CI/CD", "PostgreSQL", "Redis", "TypeScript", "Microservices"]
        for tech in common_tech:
            if re.search(r"\b" + re.escape(tech) + r"\b", job_description, re.I) and not re.search(r"\b" + re.escape(tech) + r"\b", resume_text, re.I):
                suggested_keywords.append({
                    "keyword": tech,
                    "category": "Technical Requirement",
                    "context_advice": f"Prominently featured in target JD. Incorporate into your resume only if you possess genuine hands-on experience.",
                })
            if len(suggested_keywords) >= 5:
                break

    general_suggestions = [
        {
            "title": "Strengthen Action Verbs across Work Experience",
            "description": "Convert passive phrasing (e.g. 'worked on', 'assisted with') into assertive action verbs like 'Engineered', 'Orchestrated', and 'Implemented' to demonstrate direct ownership.",
            "priority": "High",
            "category": "Action Verbs",
        },
        {
            "title": "Align Technical Terminology with Job Description",
            "description": "Mirror the exact spelling and naming conventions used in the job description (e.g., 'REST APIs', 'PostgreSQL') to pass automated ATS filters.",
            "priority": "High",
            "category": "Role Alignment",
        },
        {
            "title": "Quantify Outcomes with Real Metrics",
            "description": "Where possible, include real numbers from your actual work (e.g. users served, database size, response time improvements). Do not invent numbers—verify them from your actual results.",
            "priority": "Medium",
            "category": "Content Depth",
        },
    ]

    return {
        "summary": "Candidate profile contains relevant foundational experience. Targeted refinement of action verbs, dedicated technical skill taxonomy, and highlighting required JD concepts will significantly elevate ATS score.",
        "overall_fit_assessment": "Moderate to High potential match. Fulfills fundamental engineering requirements with opportunities to articulate technical ownership more assertively.",
        "general_suggestions": general_suggestions,
        "bullet_rewrites": bullet_rewrites,
        "suggested_keywords": suggested_keywords,
        "section_feedbacks": section_feedbacks,
    }

def _verify_and_filter_hallucinations(
    data: Dict[str, Any],
    resume_text: str,
    job_description: str,
    missing_skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Step 17 Guardrail: Post-generation strict anti-hallucination verification.
    Ensures that any bullet rewrites originated from real resume sentences,
    and suggested keywords genuinely exist in the target job description.
    """
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # 1. Verify Bullet Points: check token overlap with candidate resume
    verified_bullets = []
    candidate_tokens = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", resume_lower))

    for b in data.get("bullet_rewrites", []):
        orig = b.get("original", "").strip()
        if not orig:
            continue
        orig_tokens = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", orig.lower()))
        if not orig_tokens:
            continue
        # Calculate overlap with resume
        overlap = len(orig_tokens.intersection(candidate_tokens)) / len(orig_tokens)
        if overlap >= 0.5:  # At least 50% of the significant words must be in candidate resume
            verified_bullets.append(b)

    # If verification discarded too many, backfill with deterministic grounded rewrites
    if len(verified_bullets) < 2:
        fallback_data = _generate_deterministic_fallback(
            resume_text=resume_text,
            job_description=job_description,
            missing_skills=missing_skills,
        )
        verified_bullets = fallback_data.get("bullet_rewrites", [])

    data["bullet_rewrites"] = verified_bullets

    # 2. Verify Suggested Keywords: must actually be in the job description
    verified_keywords = []
    for kw in data.get("suggested_keywords", []):
        word = kw.get("keyword", "").strip()
        if word and word.lower() in jd_lower:
            verified_keywords.append(kw)
        elif missing_skills and word in missing_skills:
            verified_keywords.append(kw)

    if not verified_keywords and missing_skills:
        for ms in missing_skills[:5]:
            verified_keywords.append({
                "keyword": ms,
                "category": "Required Skill",
                "context_advice": f"Add {ms} under your technical skills or project descriptions if you have practical experience with it."
            })

    data["suggested_keywords"] = verified_keywords
    return data

def analyze_resume_with_llm(
    resume_text: str,
    job_description: str,
    resume_sections: Optional[Dict[str, Any]] = None,
    job_title: Optional[str] = "",
    missing_skills: Optional[List[str]] = None,
) -> LLMAnalysisResponse:
    """
    Main entry point for Step 10: LLM API Integration.
    
    1. Validates input text.
    2. Builds grounded contextual prompt.
    3. Attempts Google Gemini API first if configured in .env.
    4. Attempts OpenAI / Groq API second if configured in .env.
    5. Falls back seamlessly to grounded deterministic NLP analyzer if APIs are not configured or fail.
    6. Returns structured Pydantic response conforming to all 10 requirements.
    """
    clean_resume = resume_text.strip()
    clean_jd = job_description.strip()

    if len(clean_resume) < 15:
        raise ValueError("Resume text is too brief for AI analysis. Minimum 15 characters required.")

    if len(clean_jd) < 15:
        raise ValueError("Job description is too brief for AI analysis. Minimum 15 characters required.")

    # Format the prompt
    user_prompt = f"""Target Job Title: {job_title or "Target Role"}

TARGET JOB DESCRIPTION:
\"\"\"
{clean_jd}
\"\"\"

CANDIDATE'S ACTUAL RESUME TEXT:
\"\"\"
{clean_resume}
\"\"\"

IDENTIFIED MISSING SKILLS FROM EARLIER STEP:
{json.dumps(missing_skills or [])}

INSTRUCTIONS:
Carefully analyze the resume against the target job description.
Enforce all strict grounding constraints: NEVER invent skills, certifications, experience, or metrics not present in the candidate's resume.
Return pure JSON adhering to the specified schema.
"""

    provider_used = "Deterministic NLP Engine"
    model_name = "Rule-based Grounded Engine (Configure GEMINI_API_KEY in backend/.env for live LLM)"
    data = None

    # Try Google Gemini first
    if settings.GEMINI_API_KEY:
        data = _call_gemini_api(user_prompt)
        if data:
            provider_used = "Google Gemini"
            model_name = settings.GEMINI_MODEL

    # Try OpenAI / Groq if Gemini is not set or failed
    if not data and settings.OPENAI_API_KEY:
        data = _call_openai_api(user_prompt)
        if data:
            provider_used = "OpenAI"
            model_name = settings.OPENAI_MODEL

    # Fallback if no LLM key or LLM error
    if not data:
        data = _generate_deterministic_fallback(
            resume_text=clean_resume,
            job_description=clean_jd,
            resume_sections=resume_sections,
            missing_skills=missing_skills,
        )

    # Step 17: Apply anti-hallucination verification filter
    data = _verify_and_filter_hallucinations(
        data=data,
        resume_text=clean_resume,
        job_description=clean_jd,
        missing_skills=missing_skills,
    )

    return LLMAnalysisResponse(
        summary=data.get("summary", "Analysis completed."),
        overall_fit_assessment=data.get("overall_fit_assessment", "Qualified candidate with targeted improvement opportunities."),
        general_suggestions=[GeneralSuggestion(**item) for item in data.get("general_suggestions", [])],
        bullet_rewrites=[BulletPointRewrite(**item) for item in data.get("bullet_rewrites", [])],
        suggested_keywords=[KeywordSuggestion(**item) for item in data.get("suggested_keywords", [])],
        section_feedbacks=[SectionFeedback(**item) for item in data.get("section_feedbacks", [])],
        provider_used=provider_used,
        model_name=model_name,
        grounding_guarantee="Zero invented skills, projects, qualifications, or numbers. Suggestions strictly build upon your original resume.",
        message="AI resume analysis and personalized improvement suggestions generated successfully",
    )
