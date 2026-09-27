from pydantic import BaseModel, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.product import ProductCategory


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: ProductCategory = ProductCategory.OTHER
    sku: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    intended_use: Optional[str] = None
    target_market: Optional[str] = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: ProductCategory
    sku: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    specifications: Optional[Dict[str, Any]]
    intended_use: Optional[str]
    target_market: Optional[str]
    status: str
    created_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class ProductStandardMatchResponse(BaseModel):
    id: UUID
    product_id: UUID
    standard_id: UUID
    match_score: Optional[float]
    match_reason: Optional[str]
    is_mandatory: str
    applicability_notes: Optional[str]
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    @field_serializer('product_id')
    def serialize_product_id(self, value: UUID) -> str:
        return str(value)
    
    @field_serializer('standard_id')
    def serialize_standard_id(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class ComplianceCheckCreate(BaseModel):
    standard_id: UUID
    check_type: str = "INITIAL"


class ComplianceCheckResponse(BaseModel):
    id: UUID
    product_id: UUID
    standard_id: UUID
    check_type: str
    status: str
    overall_score: Optional[float]
    checked_at: Optional[str]
    notes: Optional[str]
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    @field_serializer('product_id')
    def serialize_product_id(self, value: UUID) -> str:
        return str(value)
    
    @field_serializer('standard_id')
    def serialize_standard_id(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class ComplianceCheckItemUpdate(BaseModel):
    status: str
    evidence: Optional[str] = None
    notes: Optional[str] = None
