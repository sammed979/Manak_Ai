from sqlalchemy import Column, String, Text, ForeignKey, Enum, LargeBinary, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel
from app.models.standard import AuthorityLevel


class DocumentType(str, enum.Enum):
    STANDARD = "STANDARD"
    CIRCULAR = "CIRCULAR"
    FAQ = "FAQ"
    GUIDELINE = "GUIDELINE"
    CERTIFICATION_INFO = "CERTIFICATION_INFO"
    LABORATORY_INFO = "LABORATORY_INFO"
    HALLMARKING_INFO = "HALLMARKING_INFO"
    OTHER = "OTHER"


class KnowledgeDocument(BaseModel):
    __tablename__ = "knowledge_documents"
    
    title = Column(String(500), nullable=False)
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    source_url = Column(String(1000))
    source_name = Column(String(200))
    authority_level = Column(Enum(AuthorityLevel), default=AuthorityLevel.UNVERIFIED)
    publication_date = Column(String(20))
    effective_date = Column(String(20))
    version = Column(String(20))
    language = Column(String(10), default="en")
    checksum = Column(String(64))
    content = Column(Text)
    file_path = Column(String(1000))
    status = Column(String(20), default="ACTIVE")
    license_notes = Column(Text)
    
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(BaseModel):
    __tablename__ = "knowledge_chunks"
    
    document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(Text)  # JSON string
    embedding = Column(LargeBinary)  # Store as binary for SQLite compatibility
    
    document = relationship("KnowledgeDocument", back_populates="chunks")


class FAQ(BaseModel):
    __tablename__ = "faqs"
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(200))
    language = Column(String(10), default="en")
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"))
    authority_level = Column(Enum(AuthorityLevel), default=AuthorityLevel.UNVERIFIED)


class Circular(BaseModel):
    __tablename__ = "circulars"
    
    circular_number = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    publication_date = Column(String(20))
    content = Column(Text)
    applicable_standards = Column(Text)  # JSON string
    authority_level = Column(Enum(AuthorityLevel), default=AuthorityLevel.OFFICIAL_BIS)
