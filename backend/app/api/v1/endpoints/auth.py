from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.mongodb import get_database
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import (
    UserSignupRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.api.deps import get_current_user

router = APIRouter()

@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration / Signup",
)
def signup_user(request: UserSignupRequest, db=Depends(get_database)):
    """
    Registers a new user:
    - Validates email uniqueness in MongoDB.
    - Hashes password securely using bcrypt.
    - Saves user record in 'users' collection.
    - Generates signed JWT Bearer access token.
    """
    normalized_email = request.email.lower().strip()

    # Check if user already exists
    existing = db.users.find_one({"email": normalized_email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in.",
        )

    # Hash password securely
    hashed_password = get_password_hash(request.password)
    now_iso = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "name": request.name.strip(),
        "email": normalized_email,
        "password_hash": hashed_password,
        "created_at": now_iso,
    }

    result = db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": user_id, "email": normalized_email, "name": request.name.strip()}
    )

    user_profile = UserResponse(
        id=user_id,
        name=request.name.strip(),
        email=normalized_email,
        created_at=now_iso,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_profile,
    )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login / Sign in",
)
def login_user(request: UserLoginRequest, db=Depends(get_database)):
    """
    Authenticates a user:
    - Finds user by email in MongoDB.
    - Verifies password against bcrypt hash.
    - Issues signed JWT access token.
    """
    normalized_email = request.email.lower().strip()
    user_doc = db.users.find_one({"email": normalized_email})

    if not user_doc or not verify_password(request.password, user_doc.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(user_doc["_id"])
    access_token = create_access_token(
        data={"sub": user_id, "email": normalized_email, "name": user_doc.get("name", "User")}
    )

    user_profile = UserResponse(
        id=user_id,
        name=user_doc.get("name", "User"),
        email=normalized_email,
        created_at=str(user_doc.get("created_at", "")),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_profile,
    )

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """Protected endpoint: Returns the profile of the currently logged-in user."""
    return current_user

