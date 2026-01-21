from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChunkInput:
    section: str
    speaker: str | None
    index: int
    text: str


def chunk_section(
    section_name: str,
    section_text: str,
    max_chars: int = 1200,
    overlap_chars: int = 200,
) -> list[ChunkInput]:
    text = section_text.strip()
    if not text:
        return []

    chunks: list[ChunkInput] = []
    start = 0
    index = 0

    while start < len(text):
        end = min(start + max_chars, len(text))
        window = text[start:end]

        last_break = window.rfind("\n\n")
        if last_break == -1:
            last_break = window.rfind(". ")

        if last_break != -1 and end != len(text):
            end = start + last_break + 1

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(ChunkInput(section=section_name, speaker=None, index=index, text=chunk_text))
            index += 1

        if end == len(text):
            break

        start = max(0, end - overlap_chars)

    return chunks

