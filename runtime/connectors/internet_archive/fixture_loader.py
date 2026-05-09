"""Load committed Internet Archive metadata fixtures without source access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("IA metadata fixture must be a JSON object.")
    return payload
