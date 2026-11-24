import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class UserSignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=60, description="User full name")
    email: str = Field(..., description="User unique email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password (at least 6 characters)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(EMAIL_REGEX, clean):
            raise ValueError("Invalid email format")
        return clean

class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(EMAIL_REGEX, clean):
            raise ValueError("Invalid email format")
        return clean

class UserResponse(BaseModel):
    id: str = Field(..., description="User identifier (MongoDB ObjectId as string)")
    name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email address")
    created_at: str = Field(..., description="Account creation timestamp")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Signed JWT Bearer access token")
    token_type: str = Field(default="bearer", description="Token type, always 'bearer'")
    user: UserResponse = Field(..., description="Authenticated user profile")
