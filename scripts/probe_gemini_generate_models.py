from __future__ import annotations

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

    candidates = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-pro",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    for m in candidates:
        try:
            r = c.models.generate_content(model=m, contents='Return ONLY JSON: {"ok": true}')
            text = r.candidates[0].content.parts[0].text
            print(f"{m}: OK -> {text[:80]}")
            return
        except Exception as e:
            print(f"{m}: FAIL -> {type(e).__name__}: {e}")

    print("No working model found.")


if __name__ == "__main__":
    main()

