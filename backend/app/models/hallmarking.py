from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel
from app.models.standard import AuthorityLevel


class HallmarkingCentre(BaseModel):
    __tablename__ = "hallmarking_centres"
    
    centre_name = Column(String(500), nullable=False)
    centre_code = Column(String(50), unique=True)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    license_number = Column(String(100))
    license_expiry = Column(String(20))
    verification_status = Column(String(20), default="UNVERIFIED")
    authority_level = Column(Enum(AuthorityLevel), default=AuthorityLevel.UNVERIFIED)
