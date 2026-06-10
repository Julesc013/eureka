"""Loader and validation helpers for reviewed artifact record gate 02."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def gate_root() -> Path:
    return Path(__file__).resolve().parent


def load_public_alpha_artifact_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "public_alpha_artifact_gate.json")


def load_gate_delta(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "gate_delta_from_gate_01.json")


def read_gate_text(name: str, root: Path | None = None) -> str:
    return ((root or gate_root()) / name).read_text(encoding="utf-8")


def validate_public_alpha_artifact_gate(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    expected = {
        "reviewed_artifact_record_count": 4,
        "verified_artifact_count": 0,
        "minimum_public_alpha_reviewed_artifact_records": 25,
        "reviewed_artifact_record_gap": 21,
        "blocked_for_user_details_count": 1,
    }
    if payload.get("status") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("gate must fail for insufficient reviewed artifact records")
    for key, value in expected.items():
        if int(payload.get(key, -1)) != value:
            errors.append(f"{key} must be {value}")
    if payload.get("public_alpha_blocked") is not True:
        errors.append("public alpha must remain blocked")
    if payload.get("dev_to_main_promotion_blocked") is not True:
        errors.append("dev to main must remain blocked")
    if payload.get("next_recommended_task") != "EXTERNAL-FULL-DISCOVERY-RERUN-03":
        errors.append("next task must be EXTERNAL-FULL-DISCOVERY-RERUN-03")
    if payload.get("source_snapshot_release_gate_after_this_task") != "stale_after_current_gate_commit":
        errors.append("source/snapshot gate must be stale after this gate commit")
    return tuple(errors)


def validate_gate_delta(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    delta = payload.get("delta")
    totals = payload.get("current_totals")
    if not isinstance(delta, Mapping):
        return ("delta must be present",)
    if not isinstance(totals, Mapping):
        return ("current_totals must be present",)
    if int(delta.get("reviewed_artifact_record_count", -1)) != 2:
        errors.append("reviewed artifact record delta must be 2")
    if int(delta.get("verified_artifact_count", -1)) != 0:
        errors.append("verified artifact delta must be 0")
    if int(totals.get("reviewed_artifact_record_count", -1)) != 4:
        errors.append("current reviewed artifact record count must be 4")
    if int(totals.get("verified_artifact_count", -1)) != 0:
        errors.append("current verified artifact count must be 0")
    if int(totals.get("reviewed_artifact_record_gap", -1)) != 21:
        errors.append("current reviewed artifact gap must be 21")
    return tuple(errors)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
