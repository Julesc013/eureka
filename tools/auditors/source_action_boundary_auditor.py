#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


UNSAFE_FIELDS = (
    "live_call_performed",
    "raw_response_committed",
    "source_cache_write_performed",
    "evidence_write_performed",
    "candidate_write_performed",
    "reviewed_index_mutated",
    "master_index_mutated",
    "operator_instance_mutated",
    "download_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def audit_boundary_report(payload: Mapping[str, Any]) -> dict[str, Any]:
    violations = [field for field in UNSAFE_FIELDS if payload.get(field) is not False]
    return {
        "schema_version": "source_action_boundary_audit.v0",
        "status": "pass" if not violations else "fail",
        "violations": violations,
    }


def load_and_audit(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return audit_boundary_report(payload)
