from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache

from google import genai

from backend.app.config import get_settings


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    settings = get_settings()
    api_key = settings.require_gemini_api_key()
    return genai.Client(api_key=api_key)

EMBED_MODEL = "text-embedding-004"


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []

    client = _get_client()
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[{"parts": [{"text": t}]} for t in texts],
    )

    return [e.values for e in response.embeddings]


def embed_query(text: str) -> list[float]:
    vectors = embed_texts([text])
    return vectors[0]

