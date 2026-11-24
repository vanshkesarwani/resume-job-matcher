import os
from pathlib import Path
from typing import List, Set
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file securely
env_file_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_file_path)

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Resume Job Matcher API")
    PROJECT_DESCRIPTION: str = "Backend API for Resume Job Matcher and ATS Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # File Upload Configuration
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".docx"}
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # Allowed CORS Origins
    _raw_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,*"
    )
    ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]

    # LLM API Configuration (Step 10)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")

    # Phase 5: Database & Authentication Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "resume_job_matcher")
    
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "resume_job_matcher_super_secure_jwt_secret_key_2026_at_least_32_chars_long"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days

settings = Settings()
# Ensure upload directory exists securely
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
