"""Load committed H11 storefront fixtures without live access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .normalizer_common import _require_fixture_boundaries


def load_h11_storefront_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    _require_fixture_boundaries(payload)
    return payload
