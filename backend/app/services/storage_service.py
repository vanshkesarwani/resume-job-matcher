import os
import re
import uuid
from pathlib import Path
from typing import Tuple
from app.core.config import settings

def save_file_securely(file_bytes: bytes, original_filename: str) -> Tuple[str, Path]:
    """
    Saves uploaded file securely to prevent directory traversal and overwrite attacks.
    Returns (file_id, file_path).
    """
    # Generate unique ID
    file_id = uuid.uuid4().hex
    
    # Sanitize original filename (remove any directory separators or dangerous characters)
    clean_name = os.path.basename(original_filename)
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean_name)
    stored_name = f"{file_id}_{safe_name}"

    # Ensure destination path is strictly inside UPLOAD_DIR
    target_path = (settings.UPLOAD_DIR / stored_name).resolve()
    if not str(target_path).startswith(str(settings.UPLOAD_DIR.resolve())):
        raise ValueError("Invalid target path: directory traversal attempt detected.")

    # Write file bytes
    with open(target_path, "wb") as f:
        f.write(file_bytes)

    # Restrict file permissions (read/write for owner only: 0o600)
    try:
        os.chmod(target_path, 0o600)
    except OSError:
        pass  # Non-POSIX filesystems may ignore

    return file_id, target_path

def delete_file_permanently(file_path: Path) -> bool:
    """
    Step 18 Security: Permanently deletes uploaded file from local filesystem.
    Validates destination directory to prevent arbitrary file deletion.
    """
    try:
        resolved = Path(file_path).resolve()
        upload_dir_resolved = settings.UPLOAD_DIR.resolve()
        if not str(resolved).startswith(str(upload_dir_resolved)):
            return False
        if resolved.exists() and resolved.is_file():
            resolved.unlink()
            return True
    except Exception:
        pass
    return False

