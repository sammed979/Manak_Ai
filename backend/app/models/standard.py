from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class StandardStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    WITHDRAWN = "WITHDRAWN"
    UNDER_REVISION = "UNDER_REVISION"
    DRAFT = "DRAFT"


class AuthorityLevel(str, enum.Enum):
    OFFICIAL_BIS = "OFFICIAL_BIS"
    OFFICIAL_GOVERNMENT = "OFFICIAL_GOVERNMENT"
    VERIFIED_SECONDARY = "VERIFIED_SECONDARY"
    UNVERIFIED = "UNVERIFIED"


class Standard(BaseModel):
    __tablename__ = "standards"
    
    standard_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    scope = Column(Text)
    status = Column(Enum(StandardStatus), default=StandardStatus.ACTIVE)
    authority_level = Column(Enum(AuthorityLevel), default=AuthorityLevel.UNVERIFIED)
    publication_date = Column(String(20))
    effective_date = Column(String(20))
    version = Column(String(20))
    category = Column(String(100))
    subcategory = Column(String(100))
    ics_code = Column(String(50))
    
    versions = relationship("StandardVersion", back_populates="standard", cascade="all, delete-orphan")
    clauses = relationship("StandardClause", back_populates="standard", cascade="all, delete-orphan")


class StandardVersion(BaseModel):
    __tablename__ = "standard_versions"
    
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"), nullable=False)
    version_number = Column(String(20), nullable=False)
    publication_date = Column(String(20))
    effective_date = Column(String(20))
    withdrawn_date = Column(String(20))
    changes_summary = Column(Text)
    
    standard = relationship("Standard", back_populates="versions")


class StandardClause(BaseModel):
    __tablename__ = "standard_clauses"
    
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"), nullable=False)
    clause_number = Column(String(50), nullable=False)
    title = Column(String(500))
    content = Column(Text)
    page_number = Column(Integer)
    
    standard = relationship("Standard", back_populates="clauses")


class Requirement(BaseModel):
    __tablename__ = "requirements"
    
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"), nullable=False)
    clause_id = Column(UUID(as_uuid=True), ForeignKey("standard_clauses.id"))
    requirement_number = Column(String(50))
    description = Column(Text, nullable=False)
    category = Column(String(100))
    
    clause = relationship("StandardClause")


class Test(BaseModel):
    __tablename__ = "tests"
    
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"), nullable=False)
    test_number = Column(String(50))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100))


class TestMethod(BaseModel):
    __tablename__ = "test_methods"
    
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.id"), nullable=False)
    method_name = Column(String(500), nullable=False)
    description = Column(Text)
    equipment_required = Column(Text)
    
    test = relationship("Test")


class CertificationScheme(BaseModel):
    __tablename__ = "certification_schemes"
    
    scheme_name = Column(String(500), nullable=False)
    description = Column(Text)
    product_category = Column(String(200))
    authority = Column(String(200))
    process_description = Column(Text)
