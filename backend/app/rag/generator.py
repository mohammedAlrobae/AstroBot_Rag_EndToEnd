"""
LLM generation using Groq (llama-3.3-70b-versatile).
Builds context from retrieved chunks and generates answers.
"""

import logging
from groq import Groq

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are AstroBot, the personal assistant for astronauts aboard NASA missions.
You have two knowledge sources:

1. NASA Artemis II Reference Guide (retrieved context) — use this for
   anything about this mission: crew, spacecraft, systems, procedures, timelines.
2. Your own space expertise — for general spaceflight questions not in the document.

Rules:
- Label every answer with [MISSION DATABASE] or [SPACE EXPERTISE]
- For database answers, always end with:
  ─────────────────────────────
  Source: Artemis II Reference Guide · Page {page_number}
  ─────────────────────────────
- For emergency keywords (emergency, failure, abort, leak, fire,
  decompression, malfunction, critical): numbered steps only, no prose,
  end with: "Contact Mission Control immediately."
- If answer not found: "I don't have verified data on this. Please consult Mission Control."
- Max 250 words. Support English and Arabic."""

MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.2
MAX_TOKENS = 1024


class Generator:
    """Generates answers using Groq LLM with retrieved context."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        logger.info(f"Generator initialized with model: {MODEL}")

    def generate(self, query: str, retrieved_chunks: list[dict]) -> str:
        """
        Generate an answer using the query and retrieved context chunks.
        """
        context = self._build_context(retrieved_chunks)

        user_message = f"{context}\n\nQuestion: {query}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return f"Error generating response: {str(e)}"

    def _build_context(self, chunks: list[dict]) -> str:
        """Build context block from retrieved chunks, including page numbers."""
        if not chunks:
            return "[CONTEXT]\nNo relevant documents found.\n[END CONTEXT]"

        lines = ["[CONTEXT]"]
        for i, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            page = metadata.get("page_number", "unknown")
            score = chunk.get("score", 0.0)
            lines.append(
                f"--- Source {i} (Page {page}, relevance: {score:.0%}) ---\n"
                f"{chunk['text']}\n"
            )
        lines.append("[END CONTEXT]")
        return "\n".join(lines)
