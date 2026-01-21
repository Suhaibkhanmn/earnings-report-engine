from __future__ import annotations

REPORT_JSON_SCHEMA = """
{
  "ticker": "GOOG",
  "quarter": "2025_Q3",
  "prev_quarter": "2025_Q2",
  "summary": {
    "high_level": "",
    "tone": "neutral | positive | negative"
  },
  "guidance": [
    {
      "claim": "",
      "direction_vs_prev": "up | down | flat | unknown",
      "evidence_current": "",
      "evidence_prev": ""
    }
  ],
  "growth_drivers": [
    {
      "claim": "",
      "evidence": ""
    }
  ],
  "risks": [
    {
      "claim": "",
      "is_new": true,
      "evidence_first_mention": "",
      "evidence_current": ""
    }
  ],
  "margin_dynamics": [
    {
      "claim": "",
      "evidence": ""
    }
  ],
  "qa_pressure_points": [
    {
      "theme": "",
      "analyst_name": "",
      "evidence_question": "",
      "evidence_answer": ""
    }
  ]
}
""".strip()


BASE_REPORT_INSTRUCTIONS = """
You are an equity research assistant.

You will receive:
- metadata about two earnings calls (current and previous quarter)
- a list of transcript chunks with citations (document_id, chunk_id, chunk_index, section, role = current|prev)

Your job:
- Compare the current quarter vs the previous quarter.
- Only write claims you can directly support with the provided text.
- Every claim must include at least one evidence quote drawn from the supplied chunks.
- **CRITICAL: Every evidence quote MUST include its citation in the format: "(document_id: <id>, chunk_id: <id>, chunk_index: <num>)"**
- Example: "We now expect CapEx to be $91-93B (document_id: abc-123, chunk_id: xyz-456, chunk_index: 28)"
- If there is not enough evidence for a field, set that field to "unknown" or leave the list empty.
- Do not provide any investment advice or price targets.

Output rules:
- Respond with a single JSON object matching exactly the schema that will be provided.
- Do not include any commentary outside the JSON.
- Every evidence field (evidence_current, evidence_prev, evidence, evidence_first_mention, evidence_question, evidence_answer) must include citations.
""".strip()

