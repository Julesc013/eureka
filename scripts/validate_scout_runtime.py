#!/usr/bin/env python3
"""Validate SCOUT-RUNTIME-00."""

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

from runtime.scout import (  # noqa: E402
    RELATED_PATH_KINDS,
    RELATION_TYPES,
    WORKUNIT_SEED_TYPES,
    build_scout_boundary_report,
    build_scout_run,
    load_candidate_index_from_examples,
    project_scout_results,
)


REQUIRED_CONTRACTS = [
    "contracts/scout/scout_run.v0.json",
    "contracts/scout/scout_relation.v0.json",
    "contracts/scout/discovery_trail.v0.json",
    "contracts/scout/related_path_packet.v0.json",
    "contracts/scout/source_trust_observation.v0.json",
    "contracts/scout/scout_workunit_seed.v0.json",
    "contracts/scout/scout_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/scout_runtime_policy.json",
    "control/policies/scout_relation_policy.json",
    "control/policies/scout_trail_policy.json",
    "control/policies/scout_source_trust_policy.json",
    "control/policies/scout_workunit_seed_policy.json",
    "control/policies/scout_non_claim_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/scout_runtime_input_state.json",
    "control/inventory/scout_contract_authority_matrix.json",
    "control/inventory/scout_relation_matrix.json",
    "control/inventory/scout_trail_matrix.json",
    "control/inventory/scout_related_path_matrix.json",
    "control/inventory/scout_source_trust_matrix.json",
    "control/inventory/scout_workunit_seed_matrix.json",
    "control/inventory/scout_candidate_integration_matrix.json",
    "control/inventory/scout_projection_matrix.json",
    "control/inventory/scout_boundary_report.json",
]
REQUIRED_EXAMPLES = [
    "examples/scout/sample_scout_run.json",
    "examples/scout/sample_relations.json",
    "examples/scout/sample_discovery_trail.json",
    "examples/scout/sample_related_paths.json",
    "examples/scout/sample_source_trust_observation.json",
    "examples/scout/sample_workunit_seeds.json",
    "examples/scout/sample_boundary_report.json",
]
REQUIRED_CLI = [
    "scripts/eureka_scout_runtime.py",
    "scripts/eureka_scout_trails.py",
    "scripts/eureka_scout_relations.py",
    "scripts/eureka_scout_source_trust.py",
]
REQUIRED_DOCS = [
    "docs/architecture/SCOUT_RUNTIME.md",
    "docs/architecture/SCOUT_RELATION_EXPANSION.md",
    "docs/architecture/DISCOVERY_TRAIL_MODEL.md",
    "docs/architecture/SOURCE_TRUST_OBSERVATION.md",
    "docs/operations/SCOUT_RUNTIME_RUNBOOK.md",
    "docs/operations/POST_SCOUT_RUNTIME_PLAN.md",
    "docs/reference/SCOUT_RELATION.md",
    "docs/reference/DISCOVERY_TRAIL.md",
    "docs/reference/RELATED_PATH_PACKET.md",
    "docs/reference/SOURCE_TRUST_OBSERVATION.md",
]
REQUIRED_TRUE = [
    "scout_outputs_are_not_truth",
    "scout_does_not_accept_candidates",
    "scout_does_not_promote_records",
    "scout_does_not_mutate_reviewed_index",
    "scout_does_not_mutate_master_index",
    "scout_does_not_mutate_public_index",
    "scout_uses_local_candidates_only_by_default",
    "review_required_for_outputs",
]
REQUIRED_FALSE = [
    "live_source_calls_enabled",
    "crawling_enabled",
    "arbitrary_scraping_enabled",
    "downloads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "public_mutation_enabled",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.parse_args(argv)
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate() -> dict[str, Any]:
    checks: dict[str, bool] = {
        "contracts_exist": _paths_exist(REQUIRED_CONTRACTS),
        "policies_exist": _paths_exist(REQUIRED_POLICIES),
        "matrices_exist": _paths_exist(REQUIRED_MATRICES),
        "examples_exist": _paths_exist(REQUIRED_EXAMPLES),
        "cli_exist": _paths_exist(REQUIRED_CLI),
        "docs_exist": _paths_exist(REQUIRED_DOCS),
        "prior_results_present": _prior_results_present(),
        "policies_safe": _policies_safe(),
        "matrices_safe": _matrices_safe(),
        "cli_help_works": _cli_help_works(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, value in checks.items() if not value]
    return {
        "schema_version": "scout_runtime_validation.v0",
        "task": "SCOUT-RUNTIME-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_mutation_enabled": False,
        "live_source_call_performed": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    paths = [
        "control/inventory/candidate_index_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
        "control/inventory/source_action_kernel_result.json",
        "control/inventory/source_wave_result.json",
        "control/inventory/domain_foundation_result.json",
        "control/inventory/scout_schema_result.json",
    ]
    if not _paths_exist(paths):
        return False
    candidate = _load_json(paths[0])
    return (
        candidate.get("status") in {"pass", "pass_with_warnings"}
        and candidate.get("accepted_truth_created") is False
        and candidate.get("reviewed_index_mutated") is False
        and candidate.get("master_index_mutated") is False
        and candidate.get("public_mutation_enabled") is False
    )


def _policies_safe() -> bool:
    for path in REQUIRED_POLICIES:
        payload = _load_json(path)
        if any(payload.get(key) is not True for key in REQUIRED_TRUE if key in payload):
            return False
        if any(payload.get(key) is not False for key in REQUIRED_FALSE if key in payload):
            return False
    return True


def _matrices_safe() -> bool:
    relation_matrix = _load_json("control/inventory/scout_relation_matrix.json")
    path_matrix = _load_json("control/inventory/scout_related_path_matrix.json")
    workunit_matrix = _load_json("control/inventory/scout_workunit_seed_matrix.json")
    return (
        set(relation_matrix.get("relation_types", [])) == set(RELATION_TYPES)
        and set(path_matrix.get("related_path_kinds", [])) == set(RELATED_PATH_KINDS)
        and set(workunit_matrix.get("runtime_workunit_seed_types", [])) == set(WORKUNIT_SEED_TYPES)
        and relation_matrix.get("accepted_truth") is False
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
    candidate_index = load_candidate_index_from_examples()
    run = build_scout_run("archive_org_dtheater_candidate", candidate_index)
    projection = project_scout_results(run, "public_web")
    boundary = build_scout_boundary_report(run)
    relations = run["relations"]
    trail = run["discovery_trail"]
    related_paths = run["related_paths"]
    source_trust = run["source_trust_observations"][0]
    workunit_seeds = run["workunit_seeds"]
    return {
        "candidate_integration_works": run["seed_candidate_id"] == "archive_org_dtheater_candidate"
        and len(run["candidate_refs"]) >= 2,
        "relations_build": len(relations) >= 1
        and {item["relation_type"] for item in relations}.issubset(set(RELATION_TYPES)),
        "discovery_trails_build": trail["review_required"] is True
        and trail["accepted_truth"] is False
        and len(trail["steps"]) == len(relations),
        "related_paths_build": len(related_paths) == len(relations)
        and all(item["accepted_truth"] is False for item in related_paths),
        "source_trust_observations_build": source_trust["accepted_truth"] is False
        and source_trust["observation_value"]["accepted_evidence_count"] == 0
        and source_trust["observation_value"]["live_verified"] is False,
        "workunit_seeds_build": len(workunit_seeds) >= 1
        and all(item["creates_runtime_workunit"] is False for item in workunit_seeds),
        "public_projection_read_only": projection["accepted_truth"] is False
        and projection["public_mutation_enabled"] is False
        and "live_source_call" in projection["blocked_actions"],
        "boundary_flags_false": all(
            boundary[key] is False
            for key in (
                "accepted_truth_created",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_mutation_enabled",
                "live_source_call_performed",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
            )
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
