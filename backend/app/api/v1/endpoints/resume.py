from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.core.config import settings
from app.schemas.resume import ResumeUploadResponse
from app.services.parser_service import (
    extract_raw_text,
    detect_skills_from_text,
    parse_resume_sections,
)
from app.services.storage_service import save_file_securely
from app.db.mongodb import get_database
from app.api.deps import get_optional_current_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    summary="Upload resume and extract structured sections (PDF or DOCX)",
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    db=Depends(get_database),
):
    """
    Upload resume in PDF (parsed via PyMuPDF) or DOCX (parsed via python-docx) format.
    Validates file extension and size (max 5 MB), stores securely, and extracts structured
    information into Professional Summary, Skills, Work Experience, Projects, and Education sections.
    """
    filename = file.filename or "uploaded_resume"
    ext = Path(filename).suffix.lower()

    # 1. Validate file extension
    if ext not in settings.ALLOWED_EXTENSIONS:
        allowed_list = ", ".join(sorted(settings.ALLOWED_EXTENSIONS)).upper()
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Only {allowed_list} files are allowed.",
        )

    # 2. Read file content
    content = await file.read()
    file_size = len(content)

    # 3. Validate file size
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty. Please select a valid resume file.",
        )

    if file_size > settings.MAX_FILE_SIZE_BYTES:
        max_mb = settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the {max_mb} MB limit. Please upload a smaller file.",
        )

    # 4. Store file securely
    try:
        file_id, _ = save_file_securely(content, filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store file securely: {str(e)}",
        )

    # 5. Extract raw text with PyMuPDF (for PDF) or python-docx (for DOCX)
    try:
        extracted_text = extract_raw_text(content, filename)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Text extraction failed: {str(e)}. Please check your file.",
        )

    # 6. Parse and organize into 5 target sections
    try:
        sections = parse_resume_sections(extracted_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume sections: {str(e)}",
        )

    # 7. Aggregate detected skills
    detected_skills = sections.skills or detect_skills_from_text(extracted_text)

    # 8. Save record in MongoDB linked to user ID if authenticated
    if current_user:
        try:
            db.resumes.insert_one({
                "user_id": current_user.id,
                "file_id": file_id,
                "filename": filename,
                "file_type": ext.lstrip("."),
                "file_size": file_size,
                "detected_skills": detected_skills,
                "raw_text": extracted_text,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            # Non-blocking logging
            pass

    return ResumeUploadResponse(
        file_id=file_id,
        filename=filename,
        file_size_bytes=file_size,
        extracted_text_length=len(extracted_text),
        detected_skills=detected_skills,
        sections=sections,
        raw_text=extracted_text,
        message="Resume uploaded and text extracted successfully",
    )
