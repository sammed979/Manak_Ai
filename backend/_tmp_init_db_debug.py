import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.database.session import engine, Base
from app.models import (  # noqa: F401
    User, Organization, Standard, StandardClause, Requirement, Test, TestMethod, CertificationScheme,
    KnowledgeDocument, KnowledgeChunk, Product, ProductStandardMatch, ComplianceCheck, ComplianceCheckItem,
    Laboratory, HallmarkingCentre, Conversation, ConversationMessage, AdminAuditLog,
)

try:
    Base.metadata.create_all(bind=engine)
    print("OK: create_all")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(2)
