"""H14 fixture loader for committed synthetic Source OS rollup fixtures only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .normalizer_common import load_h14_source_discovery_fixture


def load_fixture(path: str | Path) -> dict[str, Any]:
    return load_h14_source_discovery_fixture(path)
