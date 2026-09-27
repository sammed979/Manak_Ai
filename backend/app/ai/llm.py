"""
LLM service with evidence-based response generation.

When LLM_PROVIDER=openai and a valid key is set, the real OpenAI API is used.
Otherwise the EvidenceBasedLLMService generates structured answers directly
from retrieved evidence without inventing any standards, clauses, or URLs.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.config.settings import settings

_NO_EVIDENCE_MSG = (
    "No sufficiently relevant authoritative information was found for this query "
    "in the current knowledge base. Please consult the official BIS website "
    "(https://www.bis.gov.in) or contact BIS directly for authoritative guidance."
)

_SYSTEM_PROMPT = """You are MANAK AI, an evidence-first BIS (Bureau of Indian Standards) knowledge assistant.

STRICT RULES:
1. Answer ONLY from the provided retrieved evidence. Never invent standards, clauses, IS numbers, laboratory names, certification requirements, QCOs, or URLs.
2. If the evidence is insufficient to answer confidently, say exactly: "I could not find sufficient authoritative evidence to answer this confidently. Please verify with official BIS sources at https://www.bis.gov.in"
3. Always cite the source (IS number, clause, document title) when making a claim.
4. Use "Potentially Relevant" rather than claiming mandatory applicability unless the evidence explicitly states it is mandatory/compulsory.
5. Preserve IS numbers, clause numbers, and technical identifiers exactly as they appear in the evidence.
6. Never claim a product requires BIS certification unless the evidence explicitly states it is under a QCO or mandatory certification scheme.
"""


class LLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        pass


class EvidenceBasedLLMService(LLMService):
    """
    Generates answers directly from retrieved evidence chunks without
    calling any external API.  Enforces the no-hallucination policy by
    construction — it only assembles text from the evidence passed to it.
    """

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # The prompt is built by RAGEngine._build_prompt which embeds the
        # evidence.  We parse it back out here.
        return self._synthesise_from_prompt(prompt)

    async def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        answer = self._synthesise_from_prompt(prompt)
        return {"answer": answer}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _synthesise_from_prompt(self, prompt: str) -> str:
        """
        Extract evidence blocks from the prompt and build a structured answer.
        The RAGEngine embeds evidence as 'Source N:\\n<content>' blocks.
        """
        lines = prompt.split("\n")
        evidence_blocks: List[str] = []
        current_block: List[str] = []
        in_evidence = False

        for line in lines:
            if line.startswith("Source ") and ":" in line:
                if current_block:
                    evidence_blocks.append("\n".join(current_block).strip())
                    current_block = []
                in_evidence = True
            elif line.startswith("User question:"):
                if current_block:
                    evidence_blocks.append("\n".join(current_block).strip())
                    current_block = []
                in_evidence = False
            elif in_evidence:
                current_block.append(line)

        if current_block:
            evidence_blocks.append("\n".join(current_block).strip())

        if not evidence_blocks or all(not b for b in evidence_blocks):
            return _NO_EVIDENCE_MSG

        # Build answer from evidence
        parts = [
            "Based on the indexed knowledge base, here is what was found:\n"
        ]
        for i, block in enumerate(evidence_blocks, 1):
            if block:
                parts.append(f"[Source {i}] {block}")

        parts.append(
            "\n\nNote: This information is drawn from the indexed knowledge base. "
            "For authoritative and legally binding guidance, always verify with "
            "official BIS sources at https://www.bis.gov.in"
        )
        return "\n\n".join(parts)


class OpenAILLMService(LLMService):
    def __init__(self):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=settings.LLM_API_KEY)
        self._model = settings.LLM_MODEL

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = [
            {"role": "system", "content": system_prompt or _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.1,  # Low temperature for factual responses
            max_tokens=1500,
        )
        return resp.choices[0].message.content or _NO_EVIDENCE_MSG

    async def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        answer = await self.generate(prompt)
        return {"answer": answer}


# Keep old name as alias
MockLLMService = EvidenceBasedLLMService


def get_llm_service() -> LLMService:
    if settings.LLM_PROVIDER == "openai" and settings.LLM_API_KEY:
        try:
            return OpenAILLMService()
        except Exception:
            pass
    return EvidenceBasedLLMService()
