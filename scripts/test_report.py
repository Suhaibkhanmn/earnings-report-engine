import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import requests

payload = {
    "ticker": "GOOG",
    "quarter": "2025_Q3_FIX",
    "prev_quarter": "2025_Q2",
}

response = requests.post(
    "http://127.0.0.1:8001/report",
    json=payload,
    headers={"Content-Type": "application/json"},
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
