#!/usr/bin/env python3
"""Validate IA-02 TLS trust diagnostics and no-insecure-bypass policy."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS_PATH = REPO_ROOT / "control/inventory/ia_02_tls_trust_diagnosis.json"
REPAIR_DECISION_PATH = REPO_ROOT / "control/inventory/ia_02_tls_trust_repair_decision.json"
IA03_TASK_PATH = REPO_ROOT / ".aide/queue/IA-03/task.yaml"

SCAN_PATHS = (
    "runtime/source_observation/internet_archive_live_transport.py",
    "runtime/source_observation/internet_archive_live_probe.py",
    "scripts/eureka_ia_live_metadata_probe.py",
    "scripts/diagnose_python_tls_trust.py",
)
INSECURE_PATTERNS = (
    "ssl._create_unverified_context(",
    ".verify_mode = ssl.CERT_NONE",
    "context.verify_mode = ssl.CERT_NONE",
    ".check_hostname = False",
    "context.check_hostname = False",
    "verify=False",
    "verify = False",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_ia_tls_trust(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_ia_tls_trust(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    diagnosis = _load_json(DIAGNOSIS_PATH, errors)
    repair_decision = _load_json(REPAIR_DECISION_PATH, errors, required=False)
    if diagnosis:
        if diagnosis.get("verification_enabled") is not True:
            errors.append("tls_verification_not_enabled")
        if diagnosis.get("insecure_context_used") is not False:
            errors.append("insecure_context_used")
        if diagnosis.get("default_context_verify_mode") != "CERT_REQUIRED":
            errors.append("default_context_not_cert_required")
        if diagnosis.get("default_context_check_hostname") is not True:
            errors.append("default_context_hostname_check_disabled")
    _scan_for_insecure_patterns(repo_root, errors)
    _validate_no_raw_response_commit(repo_root, errors)

    tls_passed = diagnosis.get("tls_handshake_status") == "pass"
    ia03_blocked = "status: blocked" in IA03_TASK_PATH.read_text(encoding="utf-8") if IA03_TASK_PATH.exists() else False
    if not tls_passed and not ia03_blocked:
        errors.append("ia_03_not_blocked_after_tls_failure")
    if repair_decision:
        if repair_decision.get("insecure_tls_bypass_used") is not False:
            errors.append("repair_decision_insecure_bypass")
        if not tls_passed and repair_decision.get("ia_03_unblocked") is not False:
            errors.append("repair_decision_unblocked_ia03_without_tls")

    return {
        "schema_version": "ia_tls_trust_validation.v0",
        "task": "IA-02-TLS-TRUST-01",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "tls_handshake_status": diagnosis.get("tls_handshake_status", ""),
        "tls_failure_type": diagnosis.get("failure_type", ""),
        "verification_enabled": diagnosis.get("verification_enabled") is True,
        "insecure_context_used": diagnosis.get("insecure_context_used") is True,
        "rerun_live_probe_allowed": tls_passed,
        "ia_03_blocked": ia03_blocked,
    }


def _load_json(path: Path, errors: list[str], *, required: bool = True) -> Mapping[str, Any]:
    if not path.exists():
        if required:
            errors.append(f"missing_json:{path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path.relative_to(REPO_ROOT).as_posix()}:{exc}")
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _scan_for_insecure_patterns(repo_root: Path, errors: list[str]) -> None:
    for rel_path in SCAN_PATHS:
        path = repo_root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in INSECURE_PATTERNS:
            if pattern in text:
                errors.append(f"insecure_tls_pattern:{rel_path}:{pattern}")


def _validate_no_raw_response_commit(repo_root: Path, errors: list[str]) -> None:
    paths = [
        repo_root / "control/inventory/ia_live_probe_result_summary.json",
        repo_root / "control/inventory/ia_02_tls_rerun_result_summary.json",
        repo_root / "control/audits/ia-02-tls-trust-01-v0/generated/live_probe_redacted_summary.json",
    ]
    for path in paths:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if _contains_raw_body(payload):
            errors.append(f"raw_response_body_committed:{path.relative_to(repo_root).as_posix()}")


def _contains_raw_body(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in {"body_text", "raw_body", "response_body", "raw_response_body"}:
                return True
            if _contains_raw_body(item):
                return True
    if isinstance(value, list):
        return any(_contains_raw_body(item) for item in value)
    return False


if __name__ == "__main__":
    raise SystemExit(main())
