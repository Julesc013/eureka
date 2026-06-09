"""Loader and validation helpers for reviewed artifact record gate 01."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def gate_root() -> Path:
    return Path(__file__).resolve().parent


def load_public_alpha_artifact_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "public_alpha_artifact_gate.json")


def load_gate_delta(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "gate_delta_from_gate_00.json")


def read_gate_text(name: str, root: Path | None = None) -> str:
    return ((root or gate_root()) / name).read_text(encoding="utf-8")


def validate_public_alpha_artifact_gate(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    expected = {
        "reviewed_artifact_record_count": 2,
        "verified_artifact_count": 0,
        "reviewed_artifact_record_gap": 23,
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
    if payload.get("next_recommended_task") != "REVIEWED-ARTIFACT-CORPUS-BATCH-01":
        errors.append("next task must be REVIEWED-ARTIFACT-CORPUS-BATCH-01")
    return tuple(errors)


def validate_gate_delta(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    delta = payload.get("delta")
    if not isinstance(delta, Mapping):
        return ("delta must be present",)
    if int(delta.get("reviewed_artifact_record_count", -1)) != 2:
        errors.append("reviewed artifact record delta must be 2")
    if int(delta.get("verified_artifact_count", -1)) != 0:
        errors.append("verified artifact delta must be 0")
    return tuple(errors)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
