"""Fixture-only normalizer for redump_hash_sets."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h10_games_emulation_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h10_games_emulation_fixture(raw_fixture, "redump_hash_sets", policy)
