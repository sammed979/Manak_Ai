"""
Document analysis API.
Accepts file uploads, extracts text, and runs the RAG pipeline to identify
relevant standards and compliance gaps.
"""
from __future__ import annotations

import io
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.ai.embeddings import get_embedding_service
from app.ai.llm import get_llm_service
from app.database.session import get_db
from app.rag.engine import RAGEngine
from app.security.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Document Analysis"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/csv",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _extract_text_from_upload(file_bytes: bytes, content_type: str, filename: str) -> str:
    """Extract plain text from uploaded file."""
    if content_type == "text/plain" or filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="replace")

    if content_type == "application/pdf" or filename.endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
        except Exception as e:
            logger.warning("pdfplumber failed: %s", e)
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                return "\n".join(page.get_text() for page in doc)
            except Exception as e2:
                logger.warning("PyMuPDF failed: %s", e2)
                return ""

    if (
        content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or filename.endswith(".docx")
    ):
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            logger.warning("python-docx failed: %s", e)
            return ""

    return file_bytes.decode("utf-8", errors="replace")


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Upload and analyze a compliance document.
    Returns identified standards, compliance gaps, and evidence.
    """
    if file.content_type not in ALLOWED_TYPES and not any(
        file.filename.endswith(ext) for ext in [".pdf", ".docx", ".txt", ".csv"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Supported: PDF, DOCX, TXT",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10 MB.",
        )

    text = _extract_text_from_upload(file_bytes, file.content_type or "", file.filename or "")

    if not text.strip():
        return {
            "filename": file.filename,
            "file_size": len(file_bytes),
            "text_extracted": False,
            "error": "Could not extract text from this document. It may be scanned or image-based.",
            "standards_found": [],
            "analysis": None,
        }

    # Truncate for RAG (use first 3000 chars as query context)
    query_text = text[:3000]

    embedding_service = get_embedding_service()
    llm_service = get_llm_service()
    rag_engine = RAGEngine(embedding_service, llm_service, db)

    result = await rag_engine.query(
        user_query=f"Analyze this document for BIS compliance requirements: {query_text}",
        top_k=5,
        use_hybrid_search=True,
    )

    # Extract IS numbers mentioned in the document
    from app.rag.engine import extract_is_numbers
    doc_is_numbers = extract_is_numbers(text)

    return {
        "filename": file.filename,
        "file_size": len(file_bytes),
        "text_extracted": True,
        "text_length": len(text),
        "is_numbers_found": doc_is_numbers,
        "standards_found": list({
            src.get("metadata_parsed", {}).get("standard_number")
            for src in result["sources"]
            if src.get("metadata_parsed", {}).get("standard_number")
        }),
        "analysis": {
            "answer": result["answer"],
            "confidence": result["confidence"],
            "sources": result["sources"],
            "intent": result.get("intent"),
        },
        "disclaimer": (
            "This analysis is based on the indexed knowledge base. "
            "It does not constitute legal compliance certification. "
            "Verify with official BIS sources."
        ),
    }
