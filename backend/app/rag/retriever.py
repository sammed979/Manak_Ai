"""
Hybrid retriever combining:
- Semantic vector similarity (keyword-TF-IDF or OpenAI embeddings)
- BM25-style keyword scoring
- IS-number exact match boost
- Metadata-aware filtering
"""
from __future__ import annotations

import json
import math
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ai.embeddings import EmbeddingService, cosine_similarity, deserialize_embedding
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


def _bm25_score(query_tokens: List[str], doc_tokens: List[str], k1: float = 1.5, b: float = 0.75, avg_dl: float = 100.0) -> float:
    """Simplified BM25 score."""
    if not doc_tokens:
        return 0.0
    dl = len(doc_tokens)
    tf_map: Dict[str, int] = {}
    for t in doc_tokens:
        tf_map[t] = tf_map.get(t, 0) + 1

    score = 0.0
    for qt in set(query_tokens):
        tf = tf_map.get(qt, 0)
        if tf == 0:
            continue
        idf = math.log(1 + 1)  # simplified; single-corpus IDF ≈ log(2)
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * dl / avg_dl)
        score += idf * numerator / denominator

    # Normalise to [0, 1] range (cap at 5.0 raw score)
    return min(score / 5.0, 1.0)


class VectorRetriever:
    def __init__(self, embedding_service: EmbeddingService, db: Session):
        self.embedding_service = embedding_service
        self.db = db

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.embedding_service.embed_text(query)
        chunks = self.db.query(KnowledgeChunk).all()

        results = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            chunk_embedding = deserialize_embedding(chunk.embedding)
            similarity = cosine_similarity(query_embedding, chunk_embedding)

            metadata = self._parse_metadata(chunk.chunk_metadata)
            if not self._passes_filters(metadata, filters):
                continue

            results.append({
                "chunk_id": str(chunk.id),
                "content": chunk.content,
                "similarity": similarity,
                "combined_score": similarity,
                "metadata": chunk.chunk_metadata,
                "metadata_parsed": metadata,
                "document_id": str(chunk.document_id),
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    async def keyword_search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        chunks = self.db.query(KnowledgeChunk).all()
        results = []

        for chunk in chunks:
            doc_tokens = _tokenize(chunk.content)
            score = _bm25_score(query_tokens, doc_tokens)
            if score <= 0:
                continue

            metadata = self._parse_metadata(chunk.chunk_metadata)
            if not self._passes_filters(metadata, filters):
                continue

            results.append({
                "chunk_id": str(chunk.id),
                "content": chunk.content,
                "similarity": score,
                "combined_score": score,
                "metadata": chunk.chunk_metadata,
                "metadata_parsed": metadata,
                "document_id": str(chunk.document_id),
            })

        results.sort(key=lambda x: x["combined_score"], reverse=True)
        return results[:top_k]

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4,
        filters: Optional[Dict[str, Any]] = None,
        is_numbers: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        vector_results = await self.search(query, top_k=top_k * 3, filters=filters)
        keyword_results = await self.keyword_search(query, top_k=top_k * 3, filters=filters)

        combined: Dict[str, Dict[str, Any]] = {}

        for result in vector_results:
            cid = result["chunk_id"]
            if cid not in combined:
                combined[cid] = {**result, "combined_score": 0.0}
            combined[cid]["combined_score"] += result["similarity"] * vector_weight

        for result in keyword_results:
            cid = result["chunk_id"]
            if cid not in combined:
                combined[cid] = {**result, "combined_score": 0.0}
            combined[cid]["combined_score"] += result["similarity"] * keyword_weight

        # IS-number exact match boost
        if is_numbers:
            for cid, item in combined.items():
                content_upper = item["content"].upper()
                meta = item.get("metadata_parsed", {})
                std_num = str(meta.get("standard_number", "")).upper()
                for isn in is_numbers:
                    isn_upper = isn.upper().replace(" ", "")
                    if isn_upper in content_upper.replace(" ", "") or isn_upper in std_num.replace(" ", ""):
                        combined[cid]["combined_score"] = min(
                            combined[cid]["combined_score"] + 0.5, 1.0
                        )
                        break

        sorted_results = sorted(
            combined.values(), key=lambda x: x["combined_score"], reverse=True
        )
        return sorted_results[:top_k]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_metadata(self, metadata_str: Optional[str]) -> Dict[str, Any]:
        if not metadata_str:
            return {}
        try:
            return json.loads(metadata_str)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _passes_filters(
        self, metadata: Dict[str, Any], filters: Optional[Dict[str, Any]]
    ) -> bool:
        if not filters:
            return True
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True
