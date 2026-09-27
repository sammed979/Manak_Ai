from sqlalchemy import Column, String, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class AdminAuditLog(BaseModel):
    __tablename__ = "admin_audit_logs"

    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g. USER_ROLE_CHANGED, DOCUMENT_INGESTED, REINDEX, COMPLIANCE_STATUS_CHANGED
    target_type = Column(String(50))  # user, knowledge_document, product, compliance_check
    target_id = Column(String(100))  # stringified uuid or key
    detail = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
