import os
import re
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from app.schemas.job import JobExtractResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent
JOBS_STORAGE_DIR = BASE_DIR / "data" / "jobs"
JOBS_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Comprehensive taxonomy of skills and technologies for NLP extraction
SKILL_TAXONOMY = [
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", ".NET", "Go", "Golang", "Rust", "Ruby",
    "PHP", "Swift", "Kotlin", "Scala", "Dart", "R", "SQL", "HTML", "CSS", "Bash", "Shell",
    # Frontend
    "React", "React Native", "Next.js", "Vue.js", "Angular", "Svelte", "Redux", "Redux Toolkit",
    "Zustand", "Tailwind CSS", "Bootstrap", "Webpack", "Vite", "Material UI", "Sass", "Responsive Design",
    # Backend & Frameworks
    "FastAPI", "Django", "Flask", "Node.js", "Express.js", "NestJS", "Spring Boot", "ASP.NET",
    "Ruby on Rails", "Laravel", "REST APIs", "GraphQL", "gRPC", "Microservices", "Event-Driven Architecture",
    "WebSockets", "Celery",
    # Databases & Caching
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Elasticsearch", "Cassandra", "DynamoDB",
    "Oracle", "SQL Server", "Prisma", "SQLAlchemy", "ORM", "Supabase", "Firebase",
    # Cloud & DevOps
    "Docker", "Kubernetes", "AWS", "Amazon Web Services", "Google Cloud", "GCP", "Azure",
    "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins", "Terraform", "Ansible", "Linux", "Nginx",
    "Helm", "ArgoCD", "Datadog", "Prometheus", "Grafana",
    # Testing & Quality
    "Unit Testing", "Integration Testing", "Jest", "Vitest", "Pytest", "Cypress", "Selenium",
    "Playwright", "Mocha", "TDD",
    # AI/ML & Data
    "Pandas", "NumPy", "Machine Learning", "Data Analysis", "Deep Learning", "PyTorch", "TensorFlow",
    "Scikit-Learn", "Hugging Face", "LangChain", "LlamaIndex", "NLP", "Computer Vision",
    "Apache Spark", "Apache Airflow", "dbt", "Snowflake", "Databricks", "BigQuery", "Kafka", "RabbitMQ",
    # Methodologies & Concepts
    "Git", "GitHub", "GitLab", "Agile", "Scrum", "System Design", "Distributed Systems",
    "Object-Oriented Programming", "OOP", "Design Patterns", "Clean Architecture",
]

def _extract_job_title(text: str) -> str:
    """Extract job title using explicit prefixes or role noun patterns."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # 1. Look for explicit title prefix
    for line in lines[:10]:
        match = re.match(
            r"^(?:job\s+title|role|position|title)\s*[:\-–]\s*(.+)$",
            line,
            re.IGNORECASE,
        )
        if match:
            clean = match.group(1).strip()
            # Remove trailing extra info like "(Austin, TX)" or salary
            clean = re.sub(r"\s*\(.*?\)$", "", clean)
            if len(clean) >= 3 and len(clean) <= 60:
                return clean

    # 2. Look in the first 4 lines for common role titles
    role_pattern = re.compile(
        r"\b(?:senior|lead|principal|staff|junior|associate|chief|vp|director|head\s+of)?\s*"
        r"(?:full[- ]stack|frontend|backend|software|devops|cloud|data|ai|machine\s+learning|product|qa|security|mobile|web|systems|platform)?\s*"
        r"(?:engineer|developer|architect|scientist|manager|specialist|analyst|designer|administrator|consultant|lead)\b",
        re.IGNORECASE,
    )

    for line in lines[:5]:
        if len(line) <= 65:
            match = role_pattern.search(line)
            if match:
                # Return the matched line or the specific match
                clean = line.strip(" :-#*•\t")
                if len(clean) <= 60:
                    return clean
                return match.group(0).strip().title()

    return "Software Engineer"

def _extract_experience(text: str) -> str:
    """Extract required years of experience using NLP regex."""
    patterns = [
        # e.g. "4+ years of professional experience", "3 to 5 years of experience"
        re.compile(
            r"\b(\d{1,2}(?:\s*[\-\–]\s*\d{1,2})?\+?\s*(?:to\s*\d{1,2})?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:relevant|professional|hands[- ]on|industry|software|technical|direct))?\s+experience)\b",
            re.IGNORECASE,
        ),
        # e.g. "minimum 3 years" or "at least 5 years"
        re.compile(
            r"\b(?:at\s+least|minimum\s+(?:of\s+)?|min\s+)(\d{1,2}\+?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?)\b",
            re.IGNORECASE,
        ),
        # e.g. "5+ years in Python"
        re.compile(
            r"\b(\d{1,2}\+\s*(?:years?|yrs?))\b",
            re.IGNORECASE,
        ),
    ]

    for p in patterns:
        match = p.search(text)
        if match:
            raw = match.group(1).strip()
            # Clean up the output string
            return raw.replace("\n", " ").strip()

    # Check for entry level phrases
    if re.search(r"\b(?:entry[- ]level|new\s+grad(?:uate)?|junior|internship)\b", text, re.IGNORECASE):
        return "Entry Level (0-1 years)"

    return "3+ years of relevant experience (estimated)"

def _extract_skills(text: str) -> Tuple[List[str], List[str]]:
    """
    Differentiates required skills from preferred/nice-to-have skills using section
    segmentation and contextual modal indicators.
    """
    required_set = set()
    preferred_set = set()

    lines = text.splitlines()
    current_mode = "required"  # default context

    req_header_re = re.compile(
        r"^(?:requirements|required\s+qualifications|minimum\s+qualifications|qualifications|must\s+have|what\s+you(?:'ll|\s+will)\s+need|what\s+we(?:'re|\s+are)\s+looking\s+for|what\s+you\s+bring)\b",
        re.IGNORECASE,
    )
    pref_header_re = re.compile(
        r"^(?:preferred(?:\s+qualifications|\s+skills)?|nice\s+to\s+have|bonus(?:\s+points)?|plus(?:es)?|desired\s+qualifications|good\s+to\s+have)\b",
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip(" #*•-:\t")
        if not stripped:
            continue

        if req_header_re.match(stripped):
            current_mode = "required"
            continue
        elif pref_header_re.match(stripped):
            current_mode = "preferred"
            continue

        # Check line level preference cues
        line_lower = line.lower()
        is_line_preferred = (
            current_mode == "preferred"
            or "nice to have" in line_lower
            or "bonus" in line_lower
            or "plus" in line_lower
            or "preferred" in line_lower
            or "advantageous" in line_lower
            or "optional" in line_lower
        )

        for skill in SKILL_TAXONOMY:
            # Lookaround regex boundary for punctuation compatibility (C++, C#, .NET, Node.js)
            pattern = r"(?<![a-zA-Z0-9_])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9_])"
            if re.search(pattern, line_lower):
                if is_line_preferred:
                    preferred_set.add(skill)
                else:
                    required_set.add(skill)

    # Any skill marked required should take precedence over preferred
    preferred_set = preferred_set - required_set

    # Fallback if no skills were caught by mode
    if not required_set and not preferred_set:
        for skill in SKILL_TAXONOMY:
            pattern = r"(?<![a-zA-Z0-9_])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9_])"
            if re.search(pattern, text.lower()):
                required_set.add(skill)

    return sorted(list(required_set)), sorted(list(preferred_set))

def _extract_education(text: str) -> List[str]:
    """Extract education and degree requirements."""
    education_items = []
    lines = text.splitlines()

    degree_pattern = re.compile(
        r"\b(?:bachelor'?s?|master'?s?|ph\.?d\.?|doctorate|b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|degree|diploma)\b",
        re.IGNORECASE,
    )
    field_pattern = re.compile(
        r"\b(?:computer\s+science|software\s+engineering|information\s+technology|data\s+science|stem|engineering|related\s+field|equivalent\s+(?:practical\s+)?experience)\b",
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip(" *•-#\t")
        if not stripped:
            continue

        if degree_pattern.search(stripped) and (field_pattern.search(stripped) or len(stripped) < 120):
            # Clean up line
            clean = re.sub(r"^[-•*]\s*", "", stripped).strip()
            if clean and clean not in education_items and len(clean) >= 10:
                education_items.append(clean)

    if not education_items:
        # Default standard requirement
        education_items.append("Bachelor's degree in Computer Science, Engineering, or equivalent practical experience.")

    return education_items[:3]

def _extract_responsibilities(text: str) -> List[str]:
    """Extract key responsibilities and duties."""
    responsibilities = []
    lines = text.splitlines()

    in_resp_section = False
    resp_header_re = re.compile(
        r"^(?:responsibilities|key\s+responsibilities|duties|what\s+you(?:'ll|\s+will)\s+do|role\s+responsibilities|what\s+you\s+will\s+be\s+doing)\b",
        re.IGNORECASE,
    )
    other_header_re = re.compile(
        r"^(?:required|preferred|minimum|requirements|qualifications|skills|education|benefits|about\s+us|perks|compensation)\b",
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip(" *•-#\t")
        if not stripped:
            continue

        if resp_header_re.match(stripped):
            in_resp_section = True
            continue
        elif other_header_re.match(stripped) and in_resp_section:
            in_resp_section = False
            continue

        if in_resp_section:
            clean = re.sub(r"^[-•*–]\s*", "", line.strip()).strip()
            if len(clean) > 15:
                responsibilities.append(clean)

    # Fallback if no specific section was designated
    if not responsibilities:
        action_verbs_re = re.compile(
            r"^(?:design|develop|build|architect|implement|lead|collaborate|maintain|deploy|optimize|write|manage|ensure|scale)\b",
            re.IGNORECASE,
        )
        for line in lines:
            clean = re.sub(r"^[-•*–]\s*", "", line.strip()).strip()
            if action_verbs_re.match(clean) and len(clean) > 20:
                responsibilities.append(clean)

    return responsibilities[:6]

def parse_and_store_job_description(jd_text: str) -> JobExtractResponse:
    """
    Parses a Job Description using NLP extraction algorithms into structured components,
    persists it securely in JSON storage for future matching, and returns the response model.
    """
    clean_text = jd_text.strip()
    if len(clean_text) < 15:
        raise ValueError("Job description is too short. Please provide at least 15 characters of text.")

    job_id = uuid.uuid4().hex
    job_title = _extract_job_title(clean_text)
    required_skills, preferred_skills = _extract_skills(clean_text)
    experience_required = _extract_experience(clean_text)
    education_requirements = _extract_education(clean_text)
    key_responsibilities = _extract_responsibilities(clean_text)
    extracted_at = datetime.utcnow().isoformat() + "Z"

    response = JobExtractResponse(
        job_id=job_id,
        job_title=job_title,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_required=experience_required,
        education_requirements=education_requirements,
        key_responsibilities=key_responsibilities,
        raw_text=clean_text,
        extracted_at=extracted_at,
        message="Job description parsed and extracted successfully",
    )

    # Persist securely in backend storage for future resume matching
    storage_path = JOBS_STORAGE_DIR / f"{job_id}.json"
    with open(storage_path, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, indent=2, ensure_ascii=False)

    return response
