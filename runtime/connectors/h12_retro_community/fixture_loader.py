"""Load committed H12 retro/community fixtures without live access."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .normalizer_common import load_h12_retro_community_fixture as _load


def load_h12_retro_community_fixture(path: str | Path) -> dict[str, Any]:
    return _load(path)
