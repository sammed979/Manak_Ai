from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.knowledge import SearchRequest, SearchResponse, IngestRequest, KnowledgeDocumentResponse
from app.rag.engine import RAGEngine
from app.knowledge.ingestion import DocumentIngestionService
from app.ai.embeddings import get_embedding_service
from app.ai.llm import get_llm_service
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search the knowledge base using hybrid RAG with relevance threshold."""
    try:
        embedding_service = get_embedding_service()
        llm_service = get_llm_service()
        rag_engine = RAGEngine(embedding_service, llm_service, db)

        result = await rag_engine.query(
            user_query=request.query,
            top_k=request.top_k,
            use_hybrid_search=request.use_hybrid_search,
            filters=request.filters,
        )

        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.post("/ingest", response_model=KnowledgeDocumentResponse)
async def ingest_document(
    request: IngestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ingest a document into the knowledge base."""
    try:
        embedding_service = get_embedding_service()
        ingestion_service = DocumentIngestionService(embedding_service, db)

        document = await ingestion_service.ingest_text(
            title=request.title,
            content=request.content,
            document_type=request.document_type,
            source_url=request.source_url,
            source_name=request.source_name,
            authority_level=request.authority_level,
            metadata=request.metadata,
        )

        return KnowledgeDocumentResponse.model_validate(document)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all knowledge documents."""
    from app.models.knowledge import KnowledgeDocument

    documents = db.query(KnowledgeDocument).offset(skip).limit(limit).all()
    return [KnowledgeDocumentResponse.model_validate(doc) for doc in documents]
