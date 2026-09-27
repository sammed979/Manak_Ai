from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANUFACTURER = "MANUFACTURER"
    MSME = "MSME"
    CONSUMER = "CONSUMER"
    LABORATORY = "LABORATORY"
    STUDENT = "STUDENT"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.CONSUMER, nullable=False)
    is_active = Column(Boolean, default=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    
    organization = relationship("Organization", back_populates="members")
