"""Offline fixture replay helpers for connector families."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import json
from pathlib import Path
from typing import Any

from runtime.connectors.core.connector_interface import validate_no_boundary_violations
from runtime.connectors.core.output_envelope import build_connector_output_envelope


def run_fixture_replay(
    fixture_path: str | Path,
    normalizer_callable: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Replay one committed fixture through an optional normalizer."""

    fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    if not isinstance(fixture, dict):
        raise ValueError("fixture replay input must be a JSON object")
    if fixture.get("network_used") is True or fixture.get("live_call_used") is True:
        raise ValueError("fixture replay input must not claim network or live source use")
    normalized = dict(normalizer_callable(fixture)) if normalizer_callable else dict(fixture)
    validate_no_boundary_violations(normalized, policy)
    envelope = build_connector_output_envelope(
        {
            "connector_id": normalized.get("connector_id") or "generic_fixture_connector",
            "source_id": normalized.get("source_id") or "generic_fixture_source",
            "source_native_id": normalized.get("source_native_id") or normalized.get("item_identifier"),
            "output_type": "normalized_source_record",
            "normalized_record": normalized,
        },
        policy,
    )
    return build_fixture_replay_result(
        {"fixture_path": str(fixture_path), "fixture_id": fixture.get("fixture_id"), "connector_id": envelope["connector_id"], "source_id": envelope["source_id"]},
        {"normalized_record": normalized, "output_envelope": envelope},
        policy,
    )


def build_fixture_replay_result(
    inputs: Mapping[str, Any],
    outputs: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic no-network fixture replay result."""

    result = {
        "schema_version": "source_connector_fixture_replay.v0",
        "fixture_replay_id": str(inputs.get("fixture_replay_id") or "fixture_replay.generic.v0"),
        "connector_id": str(inputs.get("connector_id") or "generic_fixture_connector"),
        "source_id": str(inputs.get("source_id") or "generic_fixture_source"),
        "fixture_refs": [str(inputs.get("fixture_path") or inputs.get("fixture_ref") or "unknown_fixture")],
        "fixture_status": "committed_fixture",
        "replay_mode": "offline_fixture_replay",
        "replay_inputs": dict(inputs),
        "replay_outputs": dict(outputs),
        "expected_output_refs": list(inputs.get("expected_output_refs") or []),
        "validation_summary": {"status": "pass", "no_network_used": True, "no_live_source_used": True},
        "no_network_used": True,
        "no_live_source_used": True,
        "truth_boundary": {
            "fixture_replay_accepts_source_truth": False,
            "fixture_replay_accepts_evidence_truth": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_downloads": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
        "notes": ["Fixture replay proves parsing/normalization only; it grants no live permission."],
    }
    validate_no_boundary_violations(result, policy)
    return result
