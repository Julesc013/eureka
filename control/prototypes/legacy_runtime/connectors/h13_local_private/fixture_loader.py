"""H13 fixture loader for committed synthetic fixture files only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .normalizer_common import load_h13_local_private_fixture


def load_fixture(path: str | Path) -> dict[str, Any]:
    return load_h13_local_private_fixture(path)
