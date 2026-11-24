import re
from typing import List, Dict, Set, Tuple, Optional
from app.schemas.skills import (
    SkillMatchRequest,
    SkillMatchResponse,
    MatchedSkillDetail,
    MissingSkillDetail,
)
from app.services.parser_service import detect_skills_from_text
from app.services.job_extractor_service import _extract_skills

# Canonical dictionary mapping aliases, abbreviations, and informal names to standard skill names
SKILL_SYNONYMS: Dict[str, str] = {
    # JavaScript & TypeScript
    "js": "JavaScript",
    "javascript": "JavaScript",
    "vanilla js": "JavaScript",
    "es6": "JavaScript",
    "es6+": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react native": "React Native",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "sass": "Sass",
    "scss": "Sass",
    "redux": "Redux",
    "redux toolkit": "Redux Toolkit",
    "rtk": "Redux Toolkit",
    "zustand": "Zustand",
    # Backend & Languages
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "golang": "Go",
    "go": "Go",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
    "java": "Java",
    "ruby": "Ruby",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "php": "PHP",
    "rust": "Rust",
    # Databases & Caching
    "sql": "SQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "dynamodb": "DynamoDB",
    "elasticsearch": "Elasticsearch",
    # Cloud & DevOps
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "ci-cd": "CI/CD",
    "continuous integration": "CI/CD",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "jenkins": "Jenkins",
    "tf": "Terraform",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "linux": "Linux",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    # APIs & Architecture
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "restful apis": "REST APIs",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "microservices": "Microservices",
    "system design": "System Design",
    "distributed systems": "Distributed Systems",
    "event-driven": "Event-Driven Architecture",
    "event driven": "Event-Driven Architecture",
    "websockets": "WebSockets",
    "websocket": "WebSockets",
    "socket.io": "WebSockets",
    # Modern Frameworks & Tools
    "nestjs": "NestJS",
    "fastify": "Fastify",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "celery": "Celery",
    "sqlalchemy": "SQLAlchemy",
    "prisma": "Prisma",
    "pydantic": "Pydantic",
    "svelte": "Svelte",
    "sveltekit": "SvelteKit",
    "remix": "Remix",
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "mui": "Material UI",
    "material ui": "Material UI",
    "shadcn": "Tailwind CSS",
    # Testing
    "unit test": "Unit Testing",
    "unit testing": "Unit Testing",
    "integration test": "Integration Testing",
    "integration testing": "Integration Testing",
    "testing": "Unit Testing",
    "jest": "Jest",
    "vitest": "Vitest",
    "pytest": "Pytest",
    "cypress": "Cypress",
    "playwright": "Playwright",
    "selenium": "Selenium",
    # Data & ML
    "pandas": "Pandas",
    "numpy": "NumPy",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "data analysis": "Data Analysis",
    "deep learning": "Deep Learning",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "huggingface": "Hugging Face",
    "transformers": "Transformers",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "rag": "RAG",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "opencv": "OpenCV",
    "spark": "Apache Spark",
    "pyspark": "Apache Spark",
    "apache spark": "Apache Spark",
    "airflow": "Apache Airflow",
    "apache airflow": "Apache Airflow",
    "dbt": "dbt",
    "snowflake": "Snowflake",
    "databricks": "Databricks",
    "bigquery": "BigQuery",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "supabase": "Supabase",
    "firebase": "Firebase",
    "cassandra": "Cassandra",
    "helm": "Helm",
    "argocd": "ArgoCD",
    "datadog": "Datadog",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "nginx": "Nginx",
}

def normalize_skill(raw_skill: str) -> str:
    """
    Normalizes a skill name to its canonical form using the synonym dictionary.
    Example: 'js' -> 'JavaScript', 'K8s' -> 'Kubernetes', 'Postgres' -> 'PostgreSQL'.
    """
    clean = raw_skill.strip()
    key = clean.lower()

    # Exact match in synonyms
    if key in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[key]

    # Remove extra punctuation at edges (e.g. "React,", "(FastAPI)")
    cleaned_key = re.sub(r"^[^a-zA-Z0-9+#.]+|[^a-zA-Z0-9+#.]+$", "", key)
    if cleaned_key in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[cleaned_key]

    return clean.strip().title()

def match_skills(request: SkillMatchRequest) -> SkillMatchResponse:
    """
    Compares candidate skills against job requirements, resolving synonyms
    and categorizing matching vs missing skills into required and preferred groups.
    """
    # 1. Collect Resume Skills
    candidate_raw_skills: Set[str] = set()

    if request.resume_skills:
        for s in request.resume_skills:
            if s and s.strip():
                candidate_raw_skills.add(s.strip())

    if request.resume_text:
        detected = detect_skills_from_text(request.resume_text)
        for s in detected:
            candidate_raw_skills.add(s)

        # Check for short abbreviations like JS, TS, K8s, TF, AWS, C++, C# in raw resume text
        for abbr, canonical in SKILL_SYNONYMS.items():
            if len(abbr) <= 4:
                # Use lookarounds to safely match punctuation like C++, C#, .NET
                pattern = r"(?<![a-zA-Z0-9_])" + re.escape(abbr) + r"(?![a-zA-Z0-9_])"
                if re.search(pattern, request.resume_text, re.IGNORECASE):
                    candidate_raw_skills.add(abbr)

    # Check if any resume content was provided at all
    if not request.resume_skills and (not request.resume_text or not request.resume_text.strip()):
        raise ValueError("Please provide resume skills or resume text.")

    # 2. Collect Job Description Skills (Required & Preferred)
    req_skills_raw: Set[str] = set()
    pref_skills_raw: Set[str] = set()

    if request.required_skills:
        for s in request.required_skills:
            if s and s.strip():
                req_skills_raw.add(s.strip())

    if request.preferred_skills:
        for s in request.preferred_skills:
            if s and s.strip():
                pref_skills_raw.add(s.strip())

    # If raw JD text was passed and lists are empty, extract them using our NLP extractor
    if request.job_description and (not req_skills_raw and not pref_skills_raw):
        ext_req, ext_pref = _extract_skills(request.job_description)
        req_skills_raw.update(ext_req)
        pref_skills_raw.update(ext_pref)

    if not req_skills_raw and not pref_skills_raw:
        # Check if job description was actually provided
        if not (request.job_description and request.job_description.strip()):
            raise ValueError(
                "No job description skills could be identified. Please provide required skills or job description text."
            )

    # 3. Build Canonical Mapping for Candidate Skills
    # candidate_canonical maps: canonical_name -> original_raw_token
    candidate_canonical: Dict[str, str] = {}
    for raw in candidate_raw_skills:
        canonical = normalize_skill(raw)
        if canonical not in candidate_canonical:
            candidate_canonical[canonical] = raw

    # 4. Process Required Skills
    matched_required: List[MatchedSkillDetail] = []
    missing_required: List[MissingSkillDetail] = []
    processed_req_canonicals: Set[str] = set()

    for raw in req_skills_raw:
        canonical = normalize_skill(raw)
        if canonical in processed_req_canonicals:
            continue
        processed_req_canonicals.add(canonical)

        if canonical in candidate_canonical:
            matched_token = candidate_canonical[canonical]
            is_synonym = matched_token.lower() != canonical.lower()
            matched_required.append(
                MatchedSkillDetail(
                    skill=canonical,
                    type="required",
                    synonym_match=is_synonym,
                    matched_from=matched_token if is_synonym else None,
                )
            )
        else:
            missing_required.append(
                MissingSkillDetail(
                    skill=canonical,
                    type="required",
                    importance="Mandatory",
                )
            )

    # 5. Process Preferred Skills
    matched_preferred: List[MatchedSkillDetail] = []
    missing_preferred: List[MissingSkillDetail] = []
    processed_pref_canonicals: Set[str] = set()

    for raw in pref_skills_raw:
        canonical = normalize_skill(raw)
        # Avoid duplicate evaluation if already in required
        if canonical in processed_req_canonicals or canonical in processed_pref_canonicals:
            continue
        processed_pref_canonicals.add(canonical)

        if canonical in candidate_canonical:
            matched_token = candidate_canonical[canonical]
            is_synonym = matched_token.lower() != canonical.lower()
            matched_preferred.append(
                MatchedSkillDetail(
                    skill=canonical,
                    type="preferred",
                    synonym_match=is_synonym,
                    matched_from=matched_token if is_synonym else None,
                )
            )
        else:
            missing_preferred.append(
                MissingSkillDetail(
                    skill=canonical,
                    type="preferred",
                    importance="Bonus",
                )
            )

    # 6. Identify Additional Candidate Skills (not in JD)
    matched_canonicals = {m.skill for m in matched_required}.union(
        {m.skill for m in matched_preferred}
    )
    additional_candidate_skills = sorted(
        [c for c in candidate_canonical.keys() if c not in processed_req_canonicals and c not in processed_pref_canonicals]
    )

    # 7. Compute Match Percentages
    total_req = len(processed_req_canonicals)
    matched_req_count = len(matched_required)
    if total_req > 0:
        req_pct = int(round((matched_req_count / total_req * 100)))
    else:
        req_pct = 75 if candidate_canonical else 20

    total_pref = len(processed_pref_canonicals)
    matched_pref_count = len(matched_preferred)
    if total_pref > 0:
        pref_pct = int(round((matched_pref_count / total_pref * 100)))
    else:
        pref_pct = req_pct

    # Weighted Overall Score (75% required + 25% preferred)
    if total_pref > 0:
        overall_pct = int(round(req_pct * 0.75 + pref_pct * 0.25))
    else:
        overall_pct = req_pct

    overall_pct = max(0, min(100, overall_pct))

    # Verdict
    if overall_pct >= 80:
        verdict = "Strong Skill Match"
    elif overall_pct >= 60:
        verdict = "Moderate Skill Match"
    else:
        verdict = "Needs Skill Optimization"

    # Actionable Summary
    summary = (
        f"You match {matched_req_count} of {total_req} mandatory required skills ({req_pct}%)"
    )
    if total_pref > 0:
        summary += f" and {matched_pref_count} of {total_pref} preferred skills ({pref_pct}%)."
    else:
        summary += "."

    if missing_required:
        top_missing = ", ".join([m.skill for m in missing_required[:3]])
        summary += f" Critical gaps to highlight: {top_missing}."

    return SkillMatchResponse(
        overall_match_percentage=overall_pct,
        required_match_percentage=req_pct,
        preferred_match_percentage=pref_pct,
        verdict=verdict,
        matched_required=matched_required,
        missing_required=missing_required,
        matched_preferred=matched_preferred,
        missing_preferred=missing_preferred,
        additional_candidate_skills=additional_candidate_skills,
        total_required_count=total_req,
        total_preferred_count=total_pref,
        total_candidate_skills_count=len(candidate_canonical),
        summary=summary,
    )

