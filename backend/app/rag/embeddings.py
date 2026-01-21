from __future__ import annotations

from collections.abc import Sequence

from google import genai

from backend.app.config import get_settings


_settings = get_settings()
_client = genai.Client(api_key=_settings.gemini_api_key)

EMBED_MODEL = "text-embedding-004"


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []

    response = _client.models.embed_content(
        model=EMBED_MODEL,
        contents=[{"parts": [{"text": t}]} for t in texts],
    )

    return [e.values for e in response.embeddings]


def embed_query(text: str) -> list[float]:
    vectors = embed_texts([text])
    return vectors[0]

