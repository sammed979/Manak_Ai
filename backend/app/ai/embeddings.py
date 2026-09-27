"""
Embedding service with a keyword-frequency (TF-IDF-style) fallback that
produces *semantically meaningful* vectors without an external API.

When EMBEDDING_PROVIDER=openai and a valid key is set, the real OpenAI
text-embedding model is used.  Otherwise the KeywordEmbeddingService is
used — it is NOT suitable for production but gives correct directional
similarity for BIS domain queries (e.g. "curd" will NOT match
"stainless steel water bottle").
"""
from __future__ import annotations

import math
import pickle
import re
from abc import ABC, abstractmethod
from typing import List

import numpy as np

from app.config.settings import settings

# ---------------------------------------------------------------------------
# BIS-domain vocabulary — covers the most common query terms so that
# keyword vectors are dense enough to be meaningful.
# ---------------------------------------------------------------------------
_BIS_VOCAB: List[str] = [
    # Food & dairy
    "curd", "dahi", "milk", "dairy", "food", "beverage", "edible", "consumable",
    "packaged", "pasteurised", "fermented", "yogurt", "cheese", "butter", "ghee",
    "cream", "ice", "frozen", "cereal", "grain", "wheat", "rice", "flour",
    "oil", "fat", "sugar", "salt", "spice", "condiment", "sauce", "pickle",
    "jam", "honey", "chocolate", "confectionery", "biscuit", "bread", "noodle",
    # Metals & materials
    "stainless", "steel", "iron", "aluminium", "aluminum", "copper", "zinc",
    "brass", "bronze", "alloy", "metal", "metallic", "galvanised", "coated",
    "sheet", "plate", "strip", "pipe", "tube", "wire", "rod", "bar", "section",
    # Household & consumer
    "bottle", "container", "utensil", "cookware", "vessel", "flask", "thermos",
    "cup", "glass", "plate", "bowl", "spoon", "fork", "knife", "cutlery",
    "appliance", "household", "domestic", "consumer", "kitchen",
    # Electrical
    "electrical", "electric", "voltage", "current", "power", "watt", "ampere",
    "insulation", "cable", "wire", "switch", "socket", "plug", "fuse",
    "transformer", "motor", "pump", "fan", "heater", "lamp", "bulb", "led",
    "battery", "charger", "inverter", "ups", "mcb", "rccb",
    # Construction
    "cement", "concrete", "brick", "tile", "sand", "aggregate", "rebar",
    "reinforcement", "construction", "building", "structure", "pipe", "fitting",
    # Textiles
    "textile", "fabric", "cloth", "garment", "clothing", "fibre", "fiber",
    "cotton", "polyester", "nylon", "wool", "silk", "yarn", "thread",
    # Chemicals & plastics
    "chemical", "plastic", "polymer", "pvc", "hdpe", "ldpe", "pp", "pet",
    "rubber", "adhesive", "paint", "coating", "solvent", "acid", "alkali",
    # Automotive
    "automotive", "vehicle", "car", "motorcycle", "tyre", "tire", "helmet",
    "brake", "engine", "fuel", "lubricant", "battery",
    # Precious metals
    "gold", "silver", "platinum", "hallmark", "hallmarking", "jewellery",
    "jewelry", "huid", "karat", "carat", "purity",
    # BIS / certification
    "bis", "bureau", "indian", "standard", "is", "certification", "certificate",
    "license", "licence", "mark", "isi", "compulsory", "mandatory", "voluntary",
    "qco", "quality", "control", "order", "regulation", "compliance",
    "conformity", "assessment", "testing", "test", "laboratory", "lab",
    "nabl", "accreditation", "accredited", "inspection", "audit",
    "requirement", "specification", "clause", "scope", "method", "procedure",
    "safety", "health", "environment", "performance", "dimension", "tolerance",
    "material", "composition", "grade", "type", "class", "category",
    "product", "manufacture", "manufacturer", "import", "export", "market",
    "consumer", "protection", "recall", "defect", "hazard", "risk",
]

# Build index once at module load
_VOCAB_INDEX: dict[str, int] = {w: i for i, w in enumerate(_BIS_VOCAB)}
_VOCAB_SIZE = len(_BIS_VOCAB)


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


def _keyword_vector(text: str) -> List[float]:
    """
    Build a normalised term-frequency vector over the BIS vocabulary.
    Unknown words are ignored (they don't contribute to similarity).
    """
    tokens = _tokenize(text)
    vec = [0.0] * _VOCAB_SIZE
    for tok in tokens:
        if tok in _VOCAB_INDEX:
            vec[_VOCAB_INDEX[tok]] += 1.0
    # L2-normalise
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class EmbeddingService(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass


# ---------------------------------------------------------------------------
# Keyword-based fallback (no API key required)
# ---------------------------------------------------------------------------

class KeywordEmbeddingService(EmbeddingService):
    """
    Deterministic, semantically meaningful embeddings based on BIS-domain
    vocabulary term frequencies.  Cosine similarity between "curd" and
    "stainless steel water bottle" will be 0.0 because they share no
    vocabulary terms.
    """

    async def embed_text(self, text: str) -> List[float]:
        return _keyword_vector(text)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [_keyword_vector(t) for t in texts]


# Keep the old name as an alias so existing imports don't break
MockEmbeddingService = KeywordEmbeddingService


# ---------------------------------------------------------------------------
# OpenAI embedding service
# ---------------------------------------------------------------------------

class OpenAIEmbeddingService(EmbeddingService):
    def __init__(self):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=settings.EMBEDDING_API_KEY or settings.LLM_API_KEY)
        self._model = settings.EMBEDDING_MODEL

    async def embed_text(self, text: str) -> List[float]:
        resp = await self._client.embeddings.create(input=[text], model=self._model)
        return resp.data[0].embedding

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        resp = await self._client.embeddings.create(input=texts, model=self._model)
        return [d.embedding for d in resp.data]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_embedding_service() -> EmbeddingService:
    if settings.EMBEDDING_PROVIDER == "openai" and (
        settings.EMBEDDING_API_KEY or settings.LLM_API_KEY
    ):
        try:
            return OpenAIEmbeddingService()
        except Exception:
            pass
    return KeywordEmbeddingService()


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def cosine_similarity(a: List[float], b: List[float]) -> float:
    a_np = np.array(a, dtype=np.float32)
    b_np = np.array(b, dtype=np.float32)
    dot = float(np.dot(a_np, b_np))
    norm_a = float(np.linalg.norm(a_np))
    norm_b = float(np.linalg.norm(b_np))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def serialize_embedding(embedding: List[float]) -> bytes:
    return pickle.dumps(embedding)


def deserialize_embedding(data: bytes) -> List[float]:
    return pickle.loads(data)
