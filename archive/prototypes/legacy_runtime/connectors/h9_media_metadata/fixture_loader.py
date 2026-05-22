"""Load committed H9 media metadata fixtures without external access."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def load_h9_media_metadata_fixture(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("H9 fixture must be a JSON object")
    if payload.get("schema_version") != "h9_media_metadata_fixture.v0":
        raise ValueError("H9 fixture schema_version must be h9_media_metadata_fixture.v0")
    fixture_payload = payload.get("fixture_payload")
    if not isinstance(fixture_payload, Mapping):
        raise ValueError("H9 fixture_payload must be an object")
    return dict(payload)
