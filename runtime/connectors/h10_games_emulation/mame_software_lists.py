"""Fixture-only normalizer for mame_software_lists."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h10_games_emulation_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h10_games_emulation_fixture(raw_fixture, "mame_software_lists", policy)
