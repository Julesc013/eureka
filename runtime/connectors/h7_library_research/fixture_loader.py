"""Load committed H7 library/research fixtures without live access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_h7_library_research_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"H7 fixture must be a JSON object: {fixture_path}")
    if payload.get("schema_version") != "h7_library_research_fixture.v0":
        raise ValueError(f"unsupported H7 fixture schema_version: {payload.get('schema_version')}")
    return payload
