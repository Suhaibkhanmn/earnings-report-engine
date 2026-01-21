from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from google import genai  # noqa: E402

from backend.app.config import get_settings  # noqa: E402


def main() -> None:
    s = get_settings()
    c = genai.Client(api_key=s.gemini_api_key)

    r1 = c.models.generate_content(
        model="gemini-1.5-flash",
        contents="Return ONLY JSON: {\"ok\": true}",
    )
    print("plain:", r1.candidates[0].content.parts[0].text)

    r2 = c.models.generate_content(
        model="gemini-1.5-flash",
        contents=[{"role": "user", "parts": [{"text": "Return ONLY JSON: {\"ok\": true}"}]}],
        config={"response_mime_type": "application/json"},
    )
    print("mime:", r2.candidates[0].content.parts[0].text)


if __name__ == "__main__":
    main()

