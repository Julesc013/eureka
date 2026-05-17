#!/usr/bin/env python3
"""Validate the local workbench play seed corpus."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAY_ROOT = REPO_ROOT / "examples" / "play"
POLICY_PATH = REPO_ROOT / "control" / "policies" / "play_seed_corpus_policy.json"

REQUIRED_EXAMPLE_FILES = {
    "queries": PLAY_ROOT / "demo_queries.json",
    "reviewed_records": PLAY_ROOT / "demo_reviewed_records.json",
    "absence_records": PLAY_ROOT / "demo_absence_records.json",
    "hunts": PLAY_ROOT / "demo_hunts.json",
    "search_needs": PLAY_ROOT / "demo_search_needs.json",
    "workunits": PLAY_ROOT / "demo_workunits.json",
}

KNOWN_HIT_QUERY = "sampleproject"
KNOWN_ABSENCE_QUERY = "definitely-not-present-play-00"
MEDIA_QUERY = "New York 1993 D-Theater HD demo tape original source"
EXTRACTION_QUERY = "StyleWriter 2500 Mac OS 8 driver"
HARD_SOURCE_ROUTING_QUERY = "DirectX SDK June 2010 offline installer"
COMPATIBILITY_QUERY = "last Firefox for Windows XP"
LEGACY_COMPATIBLE_QUERY = "Windows 7 compatible old app"
DEMO_SEARCH_NEED_QUERIES = (
    MEDIA_QUERY,
    EXTRACTION_QUERY,
    HARD_SOURCE_ROUTING_QUERY,
    COMPATIBILITY_QUERY,
    LEGACY_COMPATIBLE_QUERY,
)

FORBIDDEN_TRUE_FLAGS = (
    "fake_evidence_created",
    "fake_verified_records_created",
    "live_source_call_performed",
    "source_probe_executed",
    "extraction_executed",
    "model_provider_used",
    "download_install_execute_performed",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)

FORBIDDEN_RECORD_KEYS = (
    "fake_hash",
    "sha256",
    "sha1",
    "md5",
    "rights_cleared",
    "malware_safe",
    "production_ready",
    "public_launch_ready",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    result = validate_play_seed_pack(run_script_smokes=True)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_play_seed_pack(*, run_script_smokes: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy = _load_json(POLICY_PATH, errors)
    pack = load_play_pack(errors)
    _validate_policy(policy, errors)
    _validate_pack(pack, errors, warnings)
    _validate_no_instance_state_committed(errors)
    seed_dry_run = None
    smoke = None
    if run_script_smokes:
        seed_dry_run = _run_json(
            sys.executable,
            "scripts/eureka_seed_play_demo.py",
            "--instance",
            "../instances/default",
            "--dry-run",
            "--json",
        )
        if seed_dry_run["returncode"] != 0 or seed_dry_run["payload"].get("status") != "pass":
            errors.append("seed script dry-run failed")
        smoke = _run_json(
            sys.executable,
            "scripts/eureka_play_smoke.py",
            "--instance",
            "../instances/default",
            "--operator-token",
            "validator-token",
            "--json",
        )
        if smoke["returncode"] != 0 or smoke["payload"].get("status") != "pass":
            errors.append("play smoke failed")
    status = "fail" if errors else "pass"
    return {
        "schema_version": "play_seed_pack_validation.v0",
        "task": "PLAY-00",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "demo_query_pack_valid": not errors,
        "known_hit_demo_available": bool(demo_search(pack, KNOWN_HIT_QUERY)),
        "known_absence_demo_available": demo_absence(pack, KNOWN_ABSENCE_QUERY) is not None,
        "media_search_need_demo_available": _need_for_query(pack, MEDIA_QUERY) is not None,
        "extraction_search_need_demo_available": _need_for_query(pack, EXTRACTION_QUERY) is not None,
        "hard_source_routing_search_need_demo_available": _need_for_query(pack, HARD_SOURCE_ROUTING_QUERY) is not None,
        "compatibility_search_need_demo_available": _need_for_query(pack, COMPATIBILITY_QUERY) is not None,
        "legacy_compatible_search_need_demo_available": _need_for_query(pack, LEGACY_COMPATIBLE_QUERY) is not None,
        "blocked_source_probe_demo_available": bool(blocked_workunits(pack, kind="source_probe")),
        "blocked_extraction_demo_available": bool(blocked_workunits(pack, kind="extraction_task")),
        "blocked_ai_demo_available": bool(blocked_workunits(pack, kind="agent_task")),
        "seed_script_dry_run": seed_dry_run["payload"] if seed_dry_run else None,
        "play_smoke": smoke["payload"] if smoke else None,
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_play_pack(errors: list[str] | None = None) -> dict[str, Any]:
    local_errors = errors if errors is not None else []
    return {name: _load_json(path, local_errors) for name, path in REQUIRED_EXAMPLE_FILES.items()}


def build_seed_plan(pack: Mapping[str, Any]) -> dict[str, Any]:
    reviewed = _items(pack, "reviewed_records", "records")
    absences = _items(pack, "absence_records", "records")
    hunts = _items(pack, "hunts", "hunts")
    needs = _items(pack, "search_needs", "search_needs")
    workunits = _items(pack, "workunits", "workunits")
    return {
        "reviewed_records": [item["record_id"] for item in reviewed],
        "absence_records": [item["absence_id"] for item in absences],
        "hunts": [item["id"] for item in hunts],
        "search_needs": [item["id"] for item in needs],
        "workunits": [item["id"] for item in workunits],
        "blocked_workunits": [item["id"] for item in workunits if item.get("state") == "blocked"],
        "counts": {
            "reviewed_records": len(reviewed),
            "absence_records": len(absences),
            "hunts": len(hunts),
            "search_needs": len(needs),
            "workunits": len(workunits),
        },
    }


def demo_search(pack: Mapping[str, Any], query: str, *, limit: int = 10) -> list[dict[str, Any]]:
    terms = [item for item in normalize_query(query).split() if item]
    results: list[dict[str, Any]] = []
    for record in _items(pack, "reviewed_records", "records"):
        searchable = normalize_query(
            " ".join(
                [
                    str(record.get("title", "")),
                    str(record.get("description", "")),
                    str(record.get("searchable_text", "")),
                ]
            )
        )
        matched = [term for term in terms if term in searchable]
        if not matched:
            continue
        result = {
            "record_id": record["record_id"],
            "title": record["title"],
            "description": record["description"],
            "source_id": record["source_id"],
            "score": float(len(matched)) / float(max(len(terms), 1)),
            "matched_terms": matched,
            "limitations": list(record.get("limitations", [])),
            "warnings": list(record.get("warnings", [])),
        }
        results.append(result)
    return sorted(results, key=lambda item: (-float(item["score"]), str(item["record_id"])))[:limit]


def demo_absence(pack: Mapping[str, Any], query: str) -> dict[str, Any] | None:
    normalized = normalize_query(query)
    for record in _items(pack, "absence_records", "records"):
        if record.get("normalized_query") == normalized or normalize_query(str(record.get("query", ""))) == normalized:
            return dict(record)
    if demo_search(pack, query):
        return None
    return {
        "absence_id": "play.absence.dynamic_local.v0",
        "query": query,
        "normalized_query": normalized,
        "result_count": 0,
        "absence_scope": "play_demo_corpus_only",
        "limitations": [
            "Dynamic absence applies only to the committed play demo corpus.",
            "This is not a global nonexistence claim.",
        ],
    }


def smoke_report(instance: str, operator_token: str, base_url: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    pack = load_play_pack(errors)
    validation = validate_play_seed_pack(run_script_smokes=False)
    known_hit = demo_search(pack, KNOWN_HIT_QUERY)
    known_absence = demo_absence(pack, KNOWN_ABSENCE_QUERY)
    media_need = _need_for_query(pack, MEDIA_QUERY)
    extraction_need = _need_for_query(pack, EXTRACTION_QUERY)
    blocked_source = blocked_workunits(pack, kind="source_probe")
    blocked_extraction = blocked_workunits(pack, kind="extraction_task")
    blocked_ai = blocked_workunits(pack, kind="agent_task")
    checks = {
        "known_hit_query": bool(known_hit),
        "known_absence_query": bool(known_absence and known_absence.get("result_count") == 0),
        "media_search_need": media_need is not None,
        "extraction_search_need": extraction_need is not None,
        "demo_workunits": bool(_items(pack, "workunits", "workunits")),
        "blocked_source_probe_workunits": bool(blocked_source),
        "blocked_extraction_workunits": bool(blocked_extraction),
        "blocked_ai_workunits": bool(blocked_ai),
        "source_probe_execution_disabled": True,
        "extraction_execution_disabled": True,
        "model_provider_disabled": True,
    }
    for name, passed in checks.items():
        if not passed:
            errors.append(f"smoke check failed: {name}")
    status = "fail" if errors or validation["status"] != "pass" else "pass"
    return {
        "schema_version": "play_smoke_result.v0",
        "task": "PLAY-00",
        "status": status,
        "instance": instance,
        "base_url": base_url,
        "base_url_contacted": False,
        "operator_token_supplied": bool(operator_token),
        "checks": checks,
        "known_hit_result": known_hit[0] if known_hit else None,
        "known_absence_result": known_absence,
        "media_search_need_id": media_need.get("id") if media_need else None,
        "extraction_search_need_id": extraction_need.get("id") if extraction_need else None,
        "blocked_source_probe_workunit_ids": [item["id"] for item in blocked_source],
        "blocked_extraction_workunit_ids": [item["id"] for item in blocked_extraction],
        "blocked_ai_workunit_ids": [item["id"] for item in blocked_ai],
        "errors": errors,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def blocked_workunits(pack: Mapping[str, Any], *, kind: str | None = None) -> list[dict[str, Any]]:
    items = []
    for workunit in _items(pack, "workunits", "workunits"):
        if kind and workunit.get("kind") != kind:
            continue
        if workunit.get("state") == "blocked" and workunit.get("blocked_by_policy") is True:
            items.append(dict(workunit))
    return items


def normalize_query(query: str) -> str:
    return " ".join(str(query or "").strip().lower().split())


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "schema_version": "play_seed_corpus_policy.v0",
        "task": "PLAY-00",
        "fixture_backed_records_allowed": True,
        "reviewed_demo_records_allowed": True,
        "absence_demo_records_allowed": True,
        "search_need_demo_records_allowed": True,
        "workunit_demo_records_allowed": True,
        "provisional_candidates_allowed": True,
        "fake_evidence_forbidden": True,
        "fake_verified_records_forbidden": True,
        "fake_hashes_forbidden": True,
        "fake_rights_claims_forbidden": True,
        "fake_malware_safety_claims_forbidden": True,
        "live_source_calls_enabled": False,
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
        "model_provider_enabled": False,
        "download_install_execute_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            errors.append(f"policy {key} mismatch")


def _validate_pack(pack: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    for name, payload in pack.items():
        if not payload:
            errors.append(f"missing or empty play file: {name}")
        _validate_forbidden_true_flags(payload, errors, context=name)
    if not demo_search(pack, KNOWN_HIT_QUERY):
        errors.append("known hit query does not return a demo reviewed result")
    if demo_absence(pack, KNOWN_ABSENCE_QUERY) is None:
        errors.append("known absence query missing absence record")
    for query in DEMO_SEARCH_NEED_QUERIES:
        need = _need_for_query(pack, query)
        if need is None:
            errors.append(f"missing SearchNeed for query: {query}")
        elif need.get("verified_result_created") is not False:
            errors.append(f"SearchNeed creates a verified result: {need.get('id')}")
    reviewed_ids = {item["record_id"] for item in _items(pack, "reviewed_records", "records")}
    unresolved_need_queries = {normalize_query(item["query"]) for item in _items(pack, "search_needs", "search_needs")}
    for record in _items(pack, "reviewed_records", "records"):
        _validate_record_shape(record, errors)
        if normalize_query(str(record.get("title", ""))) in unresolved_need_queries:
            errors.append(f"unresolved SearchNeed appears as reviewed record: {record['record_id']}")
    if "play.reviewed.sampleproject.v0" not in reviewed_ids:
        errors.append("sampleproject reviewed demo record missing")
    for kind in ("source_probe", "extraction_task", "agent_task"):
        if not blocked_workunits(pack, kind=kind):
            errors.append(f"missing blocked WorkUnit kind: {kind}")
    for workunit in _items(pack, "workunits", "workunits"):
        if workunit.get("kind") in {"source_probe", "extraction_task", "agent_task"}:
            if workunit.get("state") != "blocked" or workunit.get("blocked_by_policy") is not True:
                errors.append(f"unsafe future-action WorkUnit state: {workunit.get('id')}")
        _validate_forbidden_true_flags(workunit, errors, context=str(workunit.get("id")))
    if warnings:
        return


def _validate_record_shape(record: Mapping[str, Any], errors: list[str]) -> None:
    if record.get("fixture_backed") is not True and record.get("demo_local") is not True:
        errors.append(f"reviewed demo record is not fixture backed: {record.get('record_id')}")
    if record.get("verified_external") is not False:
        errors.append(f"reviewed demo record claims external verification: {record.get('record_id')}")
    if record.get("evidence_claims") not in ([], None):
        errors.append(f"reviewed demo record contains evidence claims: {record.get('record_id')}")
    text = json.dumps(record, sort_keys=True)
    for key in FORBIDDEN_RECORD_KEYS:
        if key in text:
            errors.append(f"forbidden demo record marker {key}: {record.get('record_id')}")


def _validate_forbidden_true_flags(payload: Mapping[str, Any], errors: list[str], *, context: str) -> None:
    for key in FORBIDDEN_TRUE_FLAGS:
        if payload.get(key) is True:
            errors.append(f"{context} has forbidden true flag: {key}")


def _validate_no_instance_state_committed(errors: list[str]) -> None:
    completed = subprocess.run(
        ["git", "ls-files", "--", "eureka-instance", "instances"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode == 0 and completed.stdout.strip():
        errors.append("local instance state is tracked: " + completed.stdout.strip().replace("\n", ", "))


def _need_for_query(pack: Mapping[str, Any], query: str) -> dict[str, Any] | None:
    normalized = normalize_query(query)
    for need in _items(pack, "search_needs", "search_needs"):
        if normalize_query(str(need.get("query", ""))) == normalized:
            return dict(need)
    return None


def _items(pack: Mapping[str, Any], section: str, key: str) -> list[dict[str, Any]]:
    payload = pack.get(section)
    if not isinstance(payload, Mapping):
        return []
    value = payload.get(key)
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.relative_to(REPO_ROOT).as_posix()}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be object: {path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    return payload


def _run_json(*args: str) -> dict[str, Any]:
    completed = subprocess.run(list(args), cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"status": "fail", "stdout": completed.stdout, "stderr": completed.stderr}
    return {"returncode": completed.returncode, "payload": payload}


if __name__ == "__main__":
    raise SystemExit(main())
