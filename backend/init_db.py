"""Initialize database tables (uses models __all__ for discovery)."""
from app.database.session import engine, Base
from app.models import (  # noqa: F401  — ensures every model is imported and registered on Base.metadata
    User,
    UserRole,
    Organization,
    Standard,
    StandardStatus,
    AuthorityLevel,
    StandardVersion,
    StandardClause,
    Requirement,
    Test,
    TestMethod,
    CertificationScheme,
    KnowledgeDocument,
    KnowledgeChunk,
    DocumentType,
    FAQ,
    Circular,
    Product,
    ProductCategory,
    ProductStandardMatch,
    ComplianceCheck,
    ComplianceCheckItem,
    Laboratory,
    LabType,
    HallmarkingCentre,
    Conversation,
    ConversationMessage,
    MessageRole,
    AdminAuditLog,
)


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
