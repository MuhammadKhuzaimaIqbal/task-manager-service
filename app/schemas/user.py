from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User email",
    )
    username: Optional[str] = Field(
        None, max_length=100, description="Optional username"
    )


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Plain password to be hashed")


class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User email",
    )
    password: str = Field(..., min_length=8, description="User password")


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str
