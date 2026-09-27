from pydantic import BaseModel, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.knowledge import DocumentType, AuthorityLevel


class KnowledgeDocumentResponse(BaseModel):
    id: UUID
    title: str
    document_type: DocumentType
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    authority_level: AuthorityLevel
    status: str
    created_at: datetime

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    use_hybrid_search: bool = True
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: str
    context_used: int
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None


class IngestRequest(BaseModel):
    title: str
    content: str
    document_type: DocumentType = DocumentType.OTHER
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    authority_level: AuthorityLevel = AuthorityLevel.UNVERIFIED
    metadata: Optional[Dict[str, Any]] = None
