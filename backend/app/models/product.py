from sqlalchemy import Column, String, Text, ForeignKey, Enum, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel
from app.models.user import User


class ProductCategory(str, enum.Enum):
    ELECTRICAL = "ELECTRICAL"
    FOOD = "FOOD"
    TEXTILES = "TEXTILES"
    METALS = "METALS"
    PLASTICS = "PLASTICS"
    CONSTRUCTION = "CONSTRUCTION"
    AUTOMOTIVE = "AUTOMOTIVE"
    CHEMICALS = "CHEMICALS"
    PRECIOUS_METALS = "PRECIOUS_METALS"
    OTHER = "OTHER"


class Product(BaseModel):
    __tablename__ = "products"
    
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(Enum(ProductCategory), default=ProductCategory.OTHER)
    manufacturer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    sku = Column(String(100))
    brand = Column(String(200))
    model = Column(String(200))
    specifications = Column(JSON)  # JSON object with product specs
    intended_use = Column(Text)
    target_market = Column(String(100))
    status = Column(String(20), default="ACTIVE")
    
    manufacturer = relationship("User")
    compliance_checks = relationship("ComplianceCheck", back_populates="product", cascade="all, delete-orphan")
    standard_matches = relationship("ProductStandardMatch", back_populates="product", cascade="all, delete-orphan")


class ProductStandardMatch(BaseModel):
    __tablename__ = "product_standard_matches"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"), nullable=False)
    match_score = Column(Float)
    match_reason = Column(Text)
    is_mandatory = Column(String(10), default="UNKNOWN")  # YES, NO, UNKNOWN
    applicability_notes = Column(Text)
    
    product = relationship("Product", back_populates="standard_matches")
    standard = relationship("Standard")


class ComplianceCheck(BaseModel):
    __tablename__ = "compliance_checks"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"))
    check_type = Column(String(50))  # INITIAL, RECHECK, AUDIT
    status = Column(String(20), default="PENDING")  # PENDING, PASSED, FAILED, INCOMPLETE
    overall_score = Column(Float)
    checked_at = Column(String(20))
    checked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)
    
    product = relationship("Product", back_populates="compliance_checks")
    check_items = relationship("ComplianceCheckItem", back_populates="compliance_check", cascade="all, delete-orphan")


class ComplianceCheckItem(BaseModel):
    __tablename__ = "compliance_check_items"
    
    compliance_check_id = Column(UUID(as_uuid=True), ForeignKey("compliance_checks.id"), nullable=False)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("requirements.id"))
    clause_reference = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default="PENDING")  # PENDING, PASSED, FAILED, NOT_APPLICABLE
    evidence = Column(Text)
    notes = Column(Text)
    
    compliance_check = relationship("ComplianceCheck", back_populates="check_items")
