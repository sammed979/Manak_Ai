from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel
from app.models.standard import AuthorityLevel


class LabType(str, enum.Enum):
    NABL = "NABL"
    BIS_RECOGNIZED = "BIS_RECOGNIZED"
    GOVERNMENT = "GOVERNMENT"
    PRIVATE = "PRIVATE"
    INTERNATIONAL = "INTERNATIONAL"


class Laboratory(BaseModel):
    __tablename__ = "laboratories"
    
    name = Column(String(500), nullable=False)
    lab_type = Column(Enum(LabType), default=LabType.PRIVATE)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    website = Column(String(500))
    nabl_accreditation_number = Column(String(100))
    bis_recognition_number = Column(String(100))
    scope_of_testing = Column(Text)
    capabilities = Column(Text)  # JSON string of test capabilities
    verification_status = Column(String(20), default="UNVERIFIED")
    authority_level = Column(Enum(AuthorityLevel), default=AuthorityLevel.UNVERIFIED)
