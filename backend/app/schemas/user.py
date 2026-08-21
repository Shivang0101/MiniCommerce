import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_admin: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
