from __future__ import annotations

from dataclasses import dataclass


PreparedSectionName = str


@dataclass
class ParsedTranscript:
    sections: dict[PreparedSectionName, str]


def parse_transcript(raw_text: str) -> ParsedTranscript:
    text = raw_text.replace("\r\n", "\n")

    lower = text.lower()
    qa_markers = ["\nq&a", "\nq & a", "question-and-answer session", "questions and answers"]

    split_index = None
    for marker in qa_markers:
        idx = lower.find(marker)
        if idx != -1:
            split_index = idx
            break

    if split_index is None:
        return ParsedTranscript(sections={"prepared_remarks": text})

    prepared = text[:split_index].strip()
    qa = text[split_index:].strip()

    sections: dict[str, str] = {}
    if prepared:
        sections["prepared_remarks"] = prepared
    if qa:
        sections["qa"] = qa

    return ParsedTranscript(sections=sections)

