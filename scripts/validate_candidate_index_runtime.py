#!/usr/bin/env python3
"""Validate the CANDIDATE-INDEX-RUNTIME-00 implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.candidate_store import (  # noqa: E402
    archive_org_candidate_to_record,
    build_candidate_boundary_report,
    build_candidate_fingerprint,
    build_candidate_index_write_plan,
    build_candidate_lane_packet,
    build_candidate_review_handoff,
    dedupe_candidates,
    sample_archive_org_candidate,
    sample_candidate_index,
    search_candidates,
)
from runtime.search.query_plan import plan_query_to_source_actions  # noqa: E402


REQUIRED_CONTRACTS = [
    "contracts/candidates/README.md",
    "contracts/candidates/candidate_record.v0.json",
    "contracts/candidates/candidate_index_record.v0.json",
    "contracts/candidates/candidate_fingerprint.v0.json",
    "contracts/candidates/candidate_state.v0.json",
    "contracts/candidates/candidate_ingest_plan.v0.json",
    "contracts/candidates/candidate_index_write_plan.v0.json",
    "contracts/candidates/candidate_search_request.v0.json",
    "contracts/candidates/candidate_search_result.v0.json",
    "contracts/candidates/candidate_lane_packet.v0.json",
    "contracts/candidates/candidate_review_handoff.v0.json",
    "contracts/candidates/candidate_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/candidate_index_policy.json",
    "control/policies/candidate_persistence_policy.json",
    "control/policies/candidate_deduplication_policy.json",
    "control/policies/candidate_state_policy.json",
    "control/policies/candidate_review_handoff_policy.json",
    "control/policies/candidate_non_claim_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/candidate_record_matrix.json",
    "control/inventory/candidate_fingerprint_matrix.json",
    "control/inventory/candidate_state_matrix.json",
    "control/inventory/candidate_deduplication_matrix.json",
    "control/inventory/candidate_ingest_matrix.json",
    "control/inventory/candidate_search_lane_matrix.json",
    "control/inventory/candidate_review_handoff_matrix.json",
    "control/inventory/candidate_public_projection_matrix.json",
]
REQUIRED_EXAMPLES = [
    "examples/candidates/archive_org_dtheater_candidate.json",
    "examples/candidates/windows_7_portable_candidate.json",
    "examples/candidates/stylewriter_driver_candidate.json",
    "examples/candidates/directx_sdk_candidate.json",
    "examples/candidate_index/sample_candidate_index.json",
    "examples/candidate_index/sample_candidate_search_result.json",
    "examples/candidate_index/sample_candidate_lane_packet.json",
    "examples/candidate_index/sample_review_handoff.json",
    "examples/candidate_index/sample_boundary_report.json",
]
REQUIRED_CLI = [
    "scripts/eureka_candidate_ingest.py",
    "scripts/eureka_candidate_search.py",
    "scripts/eureka_candidate_index.py",
    "scripts/eureka_candidate_review_handoff.py",
]
REQUIRED_DOCS = [
    "docs/architecture/CANDIDATE_INDEX_RUNTIME.md",
    "docs/architecture/CANDIDATE_RECORD_MODEL.md",
    "docs/architecture/CANDIDATE_STATE_MODEL.md",
    "docs/architecture/CANDIDATE_DEDUPLICATION.md",
    "docs/operations/CANDIDATE_INDEX_RUNBOOK.md",
    "docs/operations/POST_CANDIDATE_INDEX_PLAN.md",
    "docs/reference/CANDIDATE_RECORD.md",
    "docs/reference/CANDIDATE_STATE_MACHINE.md",
    "docs/reference/CANDIDATE_LANE_PACKET.md",
]

REQUIRED_TRUE = [
    "candidates_are_not_truth",
    "candidate_index_is_not_reviewed_index",
    "candidate_persistence_operator_or_temp_only",
    "review_required_for_promotion",
]
REQUIRED_FALSE = [
    "public_candidate_mutation_enabled",
    "automatic_candidate_acceptance_enabled",
    "reviewed_index_mutation_enabled",
    "master_index_mutation_enabled",
    "accepted_truth_created",
    "downloads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "deployment_enabled",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.parse_args(argv)
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    checks["contracts_exist"] = _paths_exist(REQUIRED_CONTRACTS)
    checks["policies_exist"] = _paths_exist(REQUIRED_POLICIES)
    checks["matrices_exist"] = _paths_exist(REQUIRED_MATRICES)
    checks["examples_exist"] = _paths_exist(REQUIRED_EXAMPLES)
    checks["cli_exist"] = _paths_exist(REQUIRED_CLI)
    checks["docs_exist"] = _paths_exist(REQUIRED_DOCS)
    checks["policies_safe"] = _policies_safe()
    checks["state_matrix_safe"] = _state_matrix_safe()
    checks["cli_help_works"] = _cli_help_works()

    runtime_checks = _runtime_checks()
    checks.update(runtime_checks)
    failures = [name for name, value in checks.items() if not value]
    return {
        "schema_version": "candidate_index_runtime_validation.v0",
        "task": "CANDIDATE-INDEX-RUNTIME-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_mutation_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _policies_safe() -> bool:
    for path in REQUIRED_POLICIES:
        payload = _load_json(path)
        if any(payload.get(key) is not True for key in REQUIRED_TRUE if key in payload or path.endswith("candidate_index_policy.json")):
            return False
        if any(payload.get(key) is not False for key in REQUIRED_FALSE if key in payload or path.endswith("candidate_index_policy.json")):
            return False
    return True


def _state_matrix_safe() -> bool:
    payload = _load_json("control/inventory/candidate_state_matrix.json")
    required_states = {
        "new",
        "seen",
        "useful_lead",
        "needs_review",
        "review_item_created",
        "rejected_wrong_object",
        "rejected_wrong_version",
        "rejected_wrong_platform",
        "rejected_low_quality",
        "duplicate",
        "blocked",
        "accepted_local_reviewed",
    }
    automatic = {tuple(item) for item in payload.get("allowed_automatic_transitions", [])}
    operator = {tuple(item) for item in payload.get("operator_review_only_transitions", [])}
    return (
        set(payload.get("candidate_states", [])) == required_states
        and ("new", "seen") in automatic
        and ("needs_review", "useful_lead") in operator
        and payload.get("public_candidate_mutation_enabled") is False
    )


def _cli_help_works() -> bool:
    for path in REQUIRED_CLI:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / path), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return False
    return True


def _runtime_checks() -> dict[str, bool]:
    query = "New York 1993 D-Theater HD demo tape original source"
    plan = plan_query_to_source_actions(query)
    candidate = archive_org_candidate_to_record(sample_archive_org_candidate(query), plan)
    fingerprint = build_candidate_fingerprint(candidate)
    duplicate = dict(candidate)
    duplicate["candidate_id"] = "archive_org_dtheater_candidate_duplicate"
    dedupe = dedupe_candidates([candidate, duplicate])
    write_plan = build_candidate_index_write_plan(candidate, "temp_store")
    index = sample_candidate_index()
    search = search_candidates("D-Theater New York 1993", index)
    lane = build_candidate_lane_packet(search, "public_web")
    handoff = build_candidate_review_handoff(candidate)
    boundary = build_candidate_boundary_report("validate_candidate_index_runtime")
    return {
        "archive_org_candidate_normalization_works": candidate["accepted_truth"] is False
        and candidate["source_family"] == "internet_archive"
        and candidate["query_plan_ref"] == plan["plan_id"],
        "fingerprint_dedupe_works": bool(fingerprint["dedupe_key"])
        and dedupe["unique_count"] == 1
        and dedupe["duplicate_count"] == 1,
        "candidate_write_plan_safe": write_plan["write_allowed"] is True
        and write_plan["write_applied"] is False
        and write_plan["reviewed_index_mutated"] is False,
        "candidate_search_works": search["result_count"] >= 1 and search["accepted_truth"] is False,
        "candidate_lane_packet_safe": lane["accepted_truth"] is False
        and lane["public_mutation_enabled"] is False
        and "promote" in lane["blocked_actions"],
        "review_handoff_works": handoff["accepted_truth"] is False
        and handoff["promotion_requires_review"] is True,
        "boundary_flags_false": all(
            boundary[key] is False
            for key in (
                "accepted_truth_created",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_mutation_enabled",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
            )
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
