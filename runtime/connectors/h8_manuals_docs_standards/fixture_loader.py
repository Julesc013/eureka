"""Load committed H8 manuals/docs/standards fixtures without live access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_h8_manuals_docs_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"H8 fixture must be a JSON object: {fixture_path}")
    if payload.get("schema_version") != "h8_manuals_docs_fixture.v0":
        raise ValueError(f"unsupported H8 fixture schema_version: {payload.get('schema_version')}")
    return payload
