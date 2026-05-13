"""Load committed H6 web archive/news/event fixtures without live access."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .normalizer_common import H6_SOURCE_IDS, _require_fixture_boundaries


def load_h6_web_archive_fixture(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("H6 fixture must be a JSON object")
    fixture = dict(payload)
    source_id = fixture.get("source_id")
    if source_id not in H6_SOURCE_IDS:
        raise ValueError(f"unknown H6 fixture source_id: {source_id}")
    if "fixture_payload" not in fixture or not isinstance(fixture["fixture_payload"], Mapping):
        raise ValueError("H6 fixture must contain fixture_payload object")
    _require_fixture_boundaries(fixture)
    return fixture
