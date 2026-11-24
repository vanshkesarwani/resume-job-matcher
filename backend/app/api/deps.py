from typing import Optional, Any
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.db.mongodb import get_database
from app.core.security import decode_access_token
from app.schemas.auth import UserResponse

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)

def get_db() -> Any:
    """FastAPI dependency to get MongoDB database instance."""
    return get_database()

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Any = Depends(get_db),
) -> UserResponse:
    """
    FastAPI dependency to enforce authentication on protected endpoints.
    Extracts Bearer token from headers, verifies JWT signature, and queries user from DB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please sign in.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # Query user from MongoDB
    try:
        user_doc = None
        if ObjectId.is_valid(user_id):
            user_doc = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            user_doc = db.users.find_one({"_id": user_id})
        if not user_doc:
            user_doc = db.users.find_one({"email": payload.get("email")})
    except Exception:
        raise credentials_exception

    if not user_doc:
        raise credentials_exception

    return UserResponse(
        id=str(user_doc["_id"]),
        name=user_doc.get("name", "User"),
        email=user_doc.get("email", ""),
        created_at=str(user_doc.get("created_at", "")),
    )

def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Any = Depends(get_db),
) -> Optional[UserResponse]:
    """
    Optional authentication dependency.
    If a valid token is provided, returns UserResponse.
    If no token or invalid, returns None (does not raise 401).
    Allows endpoints to seamlessly associate records with logged-in users while remaining flexible for guests.
    """
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except Exception:
        return None

