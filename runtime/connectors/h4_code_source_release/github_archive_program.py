"""Fixture-only normalizer for github_archive_program."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.connectors.h4_code_source_release.normalizer_common import normalize_h4_code_source_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h4_code_source_fixture(raw_fixture, "github_archive_program", policy)
