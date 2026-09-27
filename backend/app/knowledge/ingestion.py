from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, DocumentType, AuthorityLevel
from app.ai.embeddings import EmbeddingService, serialize_embedding
import hashlib
import json


class DocumentIngestionService:
    def __init__(self, embedding_service: EmbeddingService, db: Session):
        self.embedding_service = embedding_service
        self.db = db
    
    async def ingest_text(
        self,
        title: str,
        content: str,
        document_type: DocumentType = DocumentType.OTHER,
        source_url: Optional[str] = None,
        source_name: Optional[str] = None,
        authority_level: AuthorityLevel = AuthorityLevel.UNVERIFIED,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> KnowledgeDocument:
        """
        Ingest a text document by chunking and embedding it
        """
        # Create document
        checksum = hashlib.sha256(content.encode()).hexdigest()
        
        document = KnowledgeDocument(
            title=title,
            document_type=document_type,
            source_url=source_url,
            source_name=source_name,
            authority_level=authority_level,
            content=content,
            checksum=checksum,
            status="ACTIVE"
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # Chunk the content
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)
        
        # Create and embed chunks
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = metadata or {}
            chunk_metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
            
            embedding = await self.embedding_service.embed_text(chunk_text)
            
            knowledge_chunk = KnowledgeChunk(
                document_id=document.id,
                chunk_number=i,
                content=chunk_text,
                chunk_metadata=json.dumps(chunk_metadata),
                embedding=serialize_embedding(embedding)
            )
            
            self.db.add(knowledge_chunk)
        
        self.db.commit()
        
        return document
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Split text into chunks (simplified without overlap for stability)
        """
        chunks = []
        text_length = len(text)
        start = 0
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end
        
        return chunks
    
    async def ingest_standard(
        self,
        standard_number: str,
        title: str,
        content: str,
        scope: Optional[str] = None,
        authority_level: AuthorityLevel = AuthorityLevel.UNVERIFIED
    ) -> KnowledgeDocument:
        """
        Ingest a standard document
        """
        metadata = {
            "standard_number": standard_number,
            "scope": scope,
            "document_type": "STANDARD"
        }
        
        return await self.ingest_text(
            title=title,
            content=content,
            document_type=DocumentType.STANDARD,
            authority_level=authority_level,
            metadata=metadata
        )
    
    async def ingest_faq(
        self,
        question: str,
        answer: str,
        category: Optional[str] = None,
        authority_level: AuthorityLevel = AuthorityLevel.UNVERIFIED
    ) -> KnowledgeDocument:
        """
        Ingest an FAQ as a document
        """
        content = f"Question: {question}\nAnswer: {answer}"
        
        metadata = {
            "question": question,
            "category": category,
            "document_type": "FAQ"
        }
        
        return await self.ingest_text(
            title=f"FAQ: {question[:50]}...",
            content=content,
            document_type=DocumentType.FAQ,
            authority_level=authority_level,
            metadata=metadata
        )
