from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.CONSUMER


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True
