"""Load committed H4 code/source/release fixtures without source access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from control.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import (
    detect_h4_product_boundary_violations,
    detect_h4_truth_boundary_violations,
)


def load_h4_code_source_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"H4 code/source fixture must be a JSON object: {fixture_path}")
    errors = validate_h4_code_source_fixture(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def validate_h4_code_source_fixture(fixture: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if fixture.get("schema_version") != "h4_code_source_fixture.v0":
        errors.append("fixture schema_version must be h4_code_source_fixture.v0")
    for key in ("fixture_id", "source_id", "connector_family", "fixture_kind", "fixture_status", "fixture_payload"):
        if key not in fixture:
            errors.append(f"fixture missing required field: {key}")
    for key in ("live_call_used", "network_used", "external_api_used", "repository_payload_included", "source_archive_payload_included", "release_asset_payload_included", "git_command_invoked", "build_tool_invoked"):
        if fixture.get(key) is not False:
            errors.append(f"{key} must be false")
    if fixture.get("fixture_public_safe") is not True:
        errors.append("fixture_public_safe must be true")
    errors.extend(detect_h4_truth_boundary_violations(fixture))
    errors.extend(detect_h4_product_boundary_violations(fixture))
    return errors
