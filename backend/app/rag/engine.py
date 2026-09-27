"""
RAG Engine with:
- Intent detection
- Query understanding (product/category/IS-number extraction)
- Relevance threshold (weak matches rejected before LLM)
- Evidence validation
- No-hallucination policy enforcement
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ai.embeddings import EmbeddingService
from app.ai.llm import LLMService, _NO_EVIDENCE_MSG
from app.rag.retriever import VectorRetriever

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
RELEVANCE_THRESHOLD = 0.15   # Minimum combined score to include a chunk
MIN_CHUNKS_FOR_ANSWER = 1    # Need at least this many chunks above threshold

# ---------------------------------------------------------------------------
# Intent taxonomy
# ---------------------------------------------------------------------------
INTENT_KEYWORDS: Dict[str, List[str]] = {
    "STANDARD_SEARCH": [
        "standard", "is number", "find standard", "search standard", "which standard",
        "what standard", "applicable standard", "relevant standard",
    ],
    "PRODUCT_STANDARD": [
        "product", "manufacture", "sell", "applicable", "for my", "for a",
        "which bis", "what bis",
    ],
    "CERTIFICATION": [
        "certification", "certificate", "certify", "license", "licence",
        "isi mark", "bis mark", "standard mark", "get certified",
    ],
    "TESTING": [
        "test", "testing", "test method", "how to test", "test procedure",
        "test requirement",
    ],
    "LABORATORY": [
        "laboratory", "lab", "testing center", "testing centre", "nabl",
        "accredited lab", "find lab", "which lab",
    ],
    "HALLMARKING": [
        "hallmark", "hallmarking", "huid", "gold", "silver", "jewellery",
        "jewelry", "precious metal",
    ],
    "DOCUMENT_ANALYSIS": ["document", "upload", "analyze", "analyse", "pdf"],
    "COMPLIANCE": [
        "compliance", "compliant", "meet requirement", "satisfy requirement",
        "comply",
    ],
    "CLAUSE_QUERY": ["clause", "section", "paragraph", "requirement number"],
    "STANDARD_COMPARISON": ["compare", "difference between", "vs", "versus", "version"],
    "RELATED_STANDARD": ["related", "similar standard", "linked standard"],
    "GENERAL_BIS": [
        "bis", "bureau of indian standards", "bureau", "indian standards",
        "what is bis",
    ],
}

IS_NUMBER_PATTERN = re.compile(
    r"\bIS\s*[:\-]?\s*(\d{1,6}(?:[:\-]\d{1,4})?(?:\s*:\s*\d{4})?)\b",
    re.IGNORECASE,
)


def detect_intent(query: str) -> str:
    q = query.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return intent
    return "UNKNOWN"


def extract_is_numbers(query: str) -> List[str]:
    return [m.group(0).strip() for m in IS_NUMBER_PATTERN.finditer(query)]


def extract_query_entities(query: str) -> Dict[str, Any]:
    """Extract product, category, IS numbers, and keywords from a query."""
    is_numbers = extract_is_numbers(query)
    intent = detect_intent(query)

    # Simple product extraction: noun phrases after "for", "of", "about"
    product_match = re.search(
        r"(?:for|of|about|standard for|standard on|applicable to)\s+([a-zA-Z\s]{3,40})",
        query,
        re.IGNORECASE,
    )
    product = product_match.group(1).strip() if product_match else None

    # Keywords: all meaningful words (>3 chars, not stopwords)
    stopwords = {
        "what", "which", "where", "when", "how", "does", "the", "and", "for",
        "are", "this", "that", "with", "from", "have", "has", "been", "will",
        "should", "would", "could", "about", "into", "over", "after",
    }
    keywords = [
        w for w in re.findall(r"[a-zA-Z]{3,}", query.lower())
        if w not in stopwords
    ]

    return {
        "intent": intent,
        "is_numbers": is_numbers,
        "product": product,
        "keywords": keywords,
    }


class RAGEngine:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        db: Session,
    ):
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.db = db
        self.retriever = VectorRetriever(embedding_service, db)

    async def query(
        self,
        user_query: str,
        top_k: int = 5,
        use_hybrid_search: bool = True,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        entities = extract_query_entities(user_query)
        intent = entities["intent"]
        is_numbers = entities["is_numbers"]

        # Boost query with extracted entities for better retrieval
        enriched_query = user_query
        if entities["product"]:
            enriched_query = f"{user_query} {entities['product']}"

        # Retrieve chunks
        if use_hybrid_search:
            chunks = await self.retriever.hybrid_search(
                enriched_query,
                top_k=top_k * 2,
                filters=filters,
                is_numbers=is_numbers,
            )
        else:
            chunks = await self.retriever.search(
                enriched_query, top_k=top_k * 2, filters=filters
            )

        # Apply relevance threshold
        relevant_chunks = [
            c for c in chunks
            if c.get("combined_score", c.get("similarity", 0)) >= RELEVANCE_THRESHOLD
        ]

        if len(relevant_chunks) < MIN_CHUNKS_FOR_ANSWER:
            return {
                "answer": _NO_EVIDENCE_MSG,
                "sources": [],
                "confidence": "INSUFFICIENT_EVIDENCE",
                "context_used": 0,
                "intent": intent,
                "entities": entities,
            }

        top_chunks = relevant_chunks[:top_k]
        context = self._build_context(top_chunks)
        prompt = self._build_prompt(user_query, context)
        answer = await self.llm_service.generate(prompt, system_prompt=None)
        confidence = self._calculate_confidence(top_chunks)

        return {
            "answer": answer,
            "sources": top_chunks,
            "confidence": confidence,
            "context_used": len(top_chunks),
            "intent": intent,
            "entities": entities,
        }

    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            meta = chunk.get("metadata_parsed", {})
            source_info = ""
            if meta.get("standard_number"):
                source_info = f" [IS {meta['standard_number']}]"
            elif meta.get("document_type"):
                source_info = f" [{meta['document_type']}]"
            parts.append(f"Source {i}{source_info}:\n{chunk['content']}")
        return "\n\n".join(parts)

    def _build_prompt(self, query: str, context: str) -> str:
        return (
            f"Context information:\n{context}\n\n"
            f"User question: {query}\n\n"
            "Based ONLY on the provided context, answer the user's question. "
            "Cite the source numbers used. "
            "If the context does not contain sufficient information, state that clearly."
        )

    def _calculate_confidence(self, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return "INSUFFICIENT_EVIDENCE"
        scores = [c.get("combined_score", c.get("similarity", 0)) for c in chunks]
        avg = sum(scores) / len(scores)
        if avg >= 0.6:
            return "HIGH"
        if avg >= 0.35:
            return "MEDIUM"
        if avg >= RELEVANCE_THRESHOLD:
            return "LOW"
        return "INSUFFICIENT_EVIDENCE"

    async def classify_intent(self, query: str) -> str:
        return detect_intent(query)
