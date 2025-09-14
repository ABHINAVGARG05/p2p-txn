from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class UserLogin(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = Field(default=None, min_length=6)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserOut(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
