import io
import re
from typing import List, Dict, Tuple, Optional
import pymupdf  # PyMuPDF
from docx import Document
from app.schemas.resume import ResumeSections

# Curated list of common technical and professional keywords
COMMON_SKILLS = [
    # Languages
    "Python", "JavaScript", "TypeScript", "React", "Next.js", "Vue.js", "Angular", "Svelte",
    "FastAPI", "Django", "Flask", "Node.js", "Express", "HTML", "CSS", "Tailwind CSS", "Bootstrap",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "DynamoDB", "Elasticsearch",
    "Docker", "Kubernetes", "AWS", "Google Cloud", "Azure", "CI/CD", "Git", "GitHub", "GitLab",
    "REST APIs", "GraphQL", "gRPC", "Microservices", "Unit Testing", "Jest", "Vitest", "Pytest",
    "Cypress", "Playwright", "Selenium", "Agile", "Scrum", "Redux", "Zustand", "System Design",
    "Linux", "Terraform", "Ansible", "Pandas", "NumPy", "Machine Learning", "Data Analysis",
    "Deep Learning", "PyTorch", "TensorFlow", "Scikit-Learn", "Hugging Face", "LangChain",
    "NLP", "Computer Vision", "Apache Spark", "Apache Airflow", "dbt", "Snowflake", "Databricks",
    "Kafka", "RabbitMQ", "Java", "C++", "C#", ".NET", "Go", "Rust", "Ruby", "Ruby on Rails",
    "PHP", "Swift", "Kotlin", "Dart", "Flutter", "React Native", "Spring Boot", "NestJS",
    "Supabase", "Firebase", "WebSockets", "Celery", "SQLAlchemy"
]

# Section header patterns
SECTION_PATTERNS = {
    "professional_summary": re.compile(
        r"^(?:\d+[\.\)]\s*)?(?:professional\s+summary|career\s+summary|executive\s+summary|summary|professional\s+profile|profile|about\s+me|career\s+objective|objective)\b[:\s-]*$",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^(?:\d+[\.\)]\s*)?(?:technical\s+skills|core\s+competencies|key\s+skills|skills\s+(?:&|and)\s+proficiencies|technologies|tools\s+(?:&|and)\s+technologies|skills\s+(?:&|and)\s+tools|skills)\b[:\s-]*$",
        re.IGNORECASE,
    ),
    "work_experience": re.compile(
        r"^(?:\d+[\.\)]\s*)?(?:work\s+experience|professional\s+experience|employment\s+history|experience|work\s+history|relevant\s+experience)\b[:\s-]*$",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"^(?:\d+[\.\)]\s*)?(?:personal\s+projects|academic\s+projects|technical\s+projects|key\s+projects|selected\s+projects|projects)\b[:\s-]*$",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^(?:\d+[\.\)]\s*)?(?:education\s+(?:&|and)\s+certifications|academic\s+background|academic\s+history|qualifications|education)\b[:\s-]*$",
        re.IGNORECASE,
    ),
}

def extract_raw_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract raw text from PDF using PyMuPDF, or from DOCX using python-docx.
    Raises ValueError with a clear message if file cannot be read.
    """
    lower = filename.lower()
    text = ""

    if lower.endswith(".pdf"):
        try:
            # Use PyMuPDF
            with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
                if doc.page_count == 0:
                    raise ValueError("The uploaded PDF has 0 pages.")
                pages = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text and page_text.strip():
                        pages.append(page_text.strip())
                text = "\n\n".join(pages).strip()
        except Exception as e:
            raise ValueError(f"PyMuPDF failed to extract text from PDF: {str(e)}")

    elif lower.endswith(".docx"):
        try:
            # Use python-docx
            doc = Document(io.BytesIO(file_bytes))
            parts = []
            for p in doc.paragraphs:
                if p.text and p.text.strip():
                    parts.append(p.text.strip())
            # Include table cells if present
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
                    if row_cells:
                        # Deduplicate repeated merged cell text in a row
                        unique_cells = []
                        for cell in row_cells:
                            if not unique_cells or cell != unique_cells[-1]:
                                unique_cells.append(cell)
                        parts.append(" | ".join(unique_cells))
            text = "\n".join(parts).strip()
        except Exception as e:
            raise ValueError(f"python-docx failed to extract text from DOCX: {str(e)}")

    else:
        # Fallback to UTF-8 / latin-1 for plain text
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="ignore")

    clean_text = text.strip()
    if not clean_text:
        raise ValueError(
            "No readable text found in file. Please ensure it is not an image-only scanned document."
        )

    return clean_text

# Backward-compatibility alias
extract_text_from_file = extract_raw_text

def detect_skills_from_text(text: str) -> List[str]:
    """Detect skills mentioned in the given text using lookaround boundary regex matching."""
    found = set()
    text_clean = text.lower()

    for skill in COMMON_SKILLS:
        # Use lookarounds to safely handle punctuation skills like C++, C#, .NET, Node.js
        pattern = r"(?<![a-zA-Z0-9_])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9_])"
        if re.search(pattern, text_clean):
            found.add(skill)

    return sorted(list(found))

def _identify_section_header(line: str) -> Optional[str]:
    """Check if a line matches any of our target section headers."""
    stripped = line.strip()
    # Headers are usually short and don't end in full sentences
    if len(stripped) == 0 or len(stripped) > 50:
        return None
    if stripped.endswith((".", "!", "?")):
        return None

    # Remove non-alphabetical prefixes like numbering, bullets, dashes
    clean_line = re.sub(r"^[\d\.\-\*\•\#\s]+", "", stripped).strip()

    for sec_name, pattern in SECTION_PATTERNS.items():
        if pattern.match(clean_line):
            return sec_name
    return None

def _clean_items_list(lines: List[str]) -> List[str]:
    """Split block of text into meaningful bullet items or structured lines."""
    items = []
    current_item = []

    bullet_pattern = re.compile(r"^[\s\t]*[•\*\-\–\—\>]\s*")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_item:
                items.append(" ".join(current_item))
                current_item = []
            continue

        if bullet_pattern.match(stripped):
            if current_item:
                items.append(" ".join(current_item))
            clean = bullet_pattern.sub("", stripped).strip()
            current_item = [clean]
        else:
            if current_item:
                current_item.append(stripped)
            else:
                current_item = [stripped]

    if current_item:
        items.append(" ".join(current_item))

    # Fallback: if no bullets were detected, return non-empty lines
    if not items:
        items = [l.strip() for l in lines if l.strip()]

    return items

def _parse_skills_section(raw_lines: List[str], full_text: str) -> List[str]:
    """Extract individual skills from the Skills section and overall text."""
    skills_set = set()

    for line in raw_lines:
        cleaned = re.sub(r"^[^:]+:\s*", "", line)  # Remove labels like "Frontend:" or "Languages:"
        # Split on commas, bullets, pipes, or semicolons
        tokens = re.split(r"[,\|•\*\-\;\n\t]+", cleaned)
        for token in tokens:
            t = token.strip()
            if 1 < len(t) <= 30 and not re.search(r"^(and|with|including|proficient|experienced)$", t, re.I):
                # Capitalize properly if needed
                skills_set.add(t)

    # Also detect any common skills found in the entire resume
    detected = detect_skills_from_text(full_text)
    for s in detected:
        skills_set.add(s)

    return sorted(list(skills_set))

def parse_resume_sections(full_text: str) -> ResumeSections:
    """
    Organizes resume text into the 5 target sections:
    1. Professional Summary
    2. Skills
    3. Work Experience
    4. Projects
    5. Education
    Handles missing or empty sections gracefully.
    """
    raw_buckets: Dict[str, List[str]] = {
        "professional_summary": [],
        "skills": [],
        "work_experience": [],
        "projects": [],
        "education": [],
    }

    current_section = None
    lines = full_text.splitlines()

    for line in lines:
        header_match = _identify_section_header(line)
        if header_match:
            current_section = header_match
            continue

        if current_section and current_section in raw_buckets:
            raw_buckets[current_section].append(line)

    # Format each section
    # 1. Professional Summary
    summary_lines = [l.strip() for l in raw_buckets["professional_summary"] if l.strip()]
    summary_text = " ".join(summary_lines).strip()

    # 2. Skills
    skills_list = _parse_skills_section(raw_buckets["skills"], full_text)

    # 3. Work Experience
    experience_list = _clean_items_list(raw_buckets["work_experience"])

    # 4. Projects
    projects_list = _clean_items_list(raw_buckets["projects"])

    # 5. Education
    education_list = _clean_items_list(raw_buckets["education"])

    # Store raw section text mapping for reference
    raw_sections = {
        k: "\n".join(v).strip() for k, v in raw_buckets.items() if v
    }

    return ResumeSections(
        professional_summary=summary_text,
        skills=skills_list,
        work_experience=experience_list,
        education=education_list,
        projects=projects_list,
        raw_sections=raw_sections,
    )
