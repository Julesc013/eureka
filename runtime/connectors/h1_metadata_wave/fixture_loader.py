"""Load committed H1 metadata-wave fixtures without source access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from runtime.connectors.h1_metadata_wave.normalizer_common import (
    detect_h1_product_boundary_violations,
    detect_h1_truth_boundary_violations,
)


def load_h1_fixture(path: str | Path) -> dict[str, Any]:
    """Load a public-safe committed H1 fixture JSON object."""

    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"H1 fixture must be a JSON object: {fixture_path}")
    errors = validate_h1_fixture(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def validate_h1_fixture(fixture: Mapping[str, Any]) -> list[str]:
    """Return fixture validation errors for the no-live boundary."""

    errors: list[str] = []
    if fixture.get("schema_version") != "h1_metadata_fixture.v0":
        errors.append("fixture schema_version must be h1_metadata_fixture.v0")
    for key in ("fixture_id", "source_id", "fixture_kind", "fixture_status", "fixture_payload"):
        if key not in fixture:
            errors.append(f"fixture missing required field: {key}")
    for key in ("live_call_used", "network_used", "external_api_used"):
        if fixture.get(key) is not False:
            errors.append(f"{key} must be false")
    if fixture.get("fixture_public_safe") is not True:
        errors.append("fixture_public_safe must be true")
    errors.extend(detect_h1_truth_boundary_violations(fixture))
    errors.extend(detect_h1_product_boundary_violations(fixture))
    return errors
