from sqlalchemy import Column, String, ForeignKey, Text, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class MessageRole(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class Conversation(BaseModel):
    __tablename__ = "conversations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), default="New Conversation")
    language = Column(String(10), default="en")
    source = Column(String(50), default="chat")  # chat | search | ...

    user = relationship("User")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at",
    )


class ConversationMessage(BaseModel):
    __tablename__ = "conversation_messages"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSON)  # list of {source, chunk_id, document_title, clause, page, ...}
    confidence = Column(String(30))  # HIGH | MEDIUM | LOW | INSUFFICIENT_EVIDENCE
    lang_fallback = Column(String(10), nullable=True)  # if translated to another lang

    conversation = relationship("Conversation", back_populates="messages")
