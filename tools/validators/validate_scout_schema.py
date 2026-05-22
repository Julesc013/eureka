#!/usr/bin/env python3
"""Validate SCOUT schema contracts, examples, policies, docs, and boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_eval.scout_schema import (  # noqa: E402
    BLOCKED_ACTIONS,
    PROJECTION_PROFILES,
    REQUIRED_DOMAIN_IDS,
    REQUIRED_FEEDBACK_EVENT_TYPES,
    REQUIRED_RELATION_TYPES,
    REQUIRED_WORKUNIT_SEED_TYPES,
    build_scout_console_view,
    load_scout_example_records,
    load_scout_seed_manifest,
    load_scout_seed_records,
    validate_discovery_candidate,
    validate_discovery_trail,
    validate_scout_seed,
    validate_source_trust_record,
)


TASK = "AIDE-BATCH-SCOUT-SCHEMA-01"
MANIFEST_PATH = "examples/scout/scout_seed_manifest.json"

REQUIRED_CONTRACTS = (
    "contracts/scout/README.md",
    "contracts/scout/scout_seed.v0.json",
    "contracts/scout/curator_relation.v0.json",
    "contracts/scout/discovery_candidate.v0.json",
    "contracts/scout/discovery_trail.v0.json",
    "contracts/scout/related_path.v0.json",
    "contracts/scout/source_trust_record.v0.json",
    "contracts/scout/source_trust_observation.v0.json",
    "contracts/scout/hunt_feedback_event.v0.json",
    "contracts/scout/workunit_seed_suggestion.v0.json",
    "contracts/scout/unresolved_path_observation.v0.json",
    "contracts/scout/scout_console_view.v0.json",
    "contracts/scout/scout_score_decomposition.v0.json",
)

REQUIRED_POLICIES = (
    "control/policies/scout_schema_policy.json",
    "control/policies/scout_non_claim_policy.json",
    "control/policies/scout_relation_policy.json",
    "control/policies/scout_source_trust_policy.json",
    "control/policies/scout_feedback_policy.json",
    "control/policies/scout_future_ai_policy.json",
)

REQUIRED_MATRICES = (
    "control/inventory/scout_contract_matrix.json",
    "control/inventory/scout_relation_type_matrix.json",
    "control/inventory/scout_seed_inventory.json",
    "control/inventory/scout_discovery_candidate_matrix.json",
    "control/inventory/scout_discovery_trail_matrix.json",
    "control/inventory/scout_source_trust_matrix.json",
    "control/inventory/scout_feedback_event_matrix.json",
    "control/inventory/scout_workunit_seed_matrix.json",
    "control/inventory/scout_domain_handoff_matrix.json",
    "control/inventory/scout_syn_handoff_matrix.json",
    "control/inventory/scout_workbench_console_matrix.json",
)

REQUIRED_DOCS = (
    "docs/architecture/SCOUT_CURATOR_GRAPH.md",
    "docs/architecture/SCOUT_DISCOVERY_TRAILS.md",
    "docs/architecture/SCOUT_SOURCE_TRUST.md",
    "docs/operations/SCOUT_SCHEMA_RUNBOOK.md",
    "docs/operations/POST_SCOUT_SCHEMA_PLAN.md",
    "docs/reference/SCOUT_DISCOVERY_CANDIDATE.md",
    "docs/reference/SCOUT_DISCOVERY_TRAIL.md",
    "docs/reference/SCOUT_SOURCE_TRUST_RECORD.md",
    "docs/reference/SCOUT_RELATION_TYPES.md",
)

FORBIDDEN_TEXT = (
    "production-ready",
    "public launch ready",
    "live source call completed",
    "source probe completed",
    "crawl completed",
    "download completed",
    "extraction completed",
    "model call completed",
    "accepted evidence truth",
    "verified record created",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate_scout_schema(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("SCOUT schema foundation validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_scout_schema(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for rel_path in (*REQUIRED_CONTRACTS, *REQUIRED_DOCS):
        if not (root / rel_path).is_file():
            errors.append(f"{rel_path}: required file is missing.")

    for rel_path in (*REQUIRED_POLICIES, *REQUIRED_MATRICES):
        payload = _load_json(root / rel_path, errors)
        if isinstance(payload, Mapping):
            payloads[rel_path] = payload

    _validate_policy(payloads.get("control/policies/scout_schema_policy.json", {}), errors)
    _validate_non_claim_policy(payloads.get("control/policies/scout_non_claim_policy.json", {}), errors)
    _validate_relation_matrix(payloads.get("control/inventory/scout_relation_type_matrix.json", {}), errors)
    _validate_matrix_values(payloads, errors)

    manifest = load_scout_seed_manifest(root / MANIFEST_PATH)
    if manifest.get("schema_version") != "scout_seed_manifest.v0":
        errors.append(f"{MANIFEST_PATH}: schema_version must be scout_seed_manifest.v0.")
    if manifest.get("seed_status") != "example_only":
        errors.append(f"{MANIFEST_PATH}: seed_status must be example_only.")
    if _mapping(manifest.get("non_claims")).get("evidence_created") is not False:
        errors.append(f"{MANIFEST_PATH}: examples must not create evidence.")

    seeds = load_scout_seed_records(root / MANIFEST_PATH)
    seed_ids = [str(seed.get("seed_id", "")) for seed in seeds]
    if len(seed_ids) < 5:
        errors.append(f"{MANIFEST_PATH}: must include at least five deterministic SCOUT seeds.")
    for seed in seeds:
        report = validate_scout_seed(seed)
        errors.extend(report["errors"])

    examples = load_scout_example_records(root)
    for report in (
        validate_discovery_candidate(_mapping(examples.get("candidate"))),
        validate_discovery_trail(_mapping(examples.get("trail"))),
        validate_source_trust_record(_mapping(examples.get("source_trust_record"))),
    ):
        errors.extend(report["errors"])

    _validate_example_record(_mapping(examples.get("related_path")), "related_path.v0", "related_path", errors)
    _validate_example_record(_mapping(examples.get("source_trust_observation")), "source_trust_observation.v0", "source_trust_observation", errors)
    _validate_example_record(_mapping(examples.get("hunt_feedback_event")), "hunt_feedback_event.v0", "hunt_feedback_event", errors)
    _validate_example_record(_mapping(examples.get("workunit_seed_suggestion")), "workunit_seed_suggestion.v0", "workunit_seed_suggestion", errors)

    for profile in PROJECTION_PROFILES:
        view = build_scout_console_view(examples, profile)
        if view.get("read_only") is not True:
            errors.append(f"{profile}: SCOUT console view must be read-only.")
        if set(view.get("blocked_actions", [])) != set(BLOCKED_ACTIONS):
            errors.append(f"{profile}: SCOUT console view must carry every blocked action.")
        if _mapping(view.get("non_claims")).get("accepted_truth_created") is not False:
            errors.append(f"{profile}: SCOUT console view must not create truth.")

    _validate_handoffs(payloads, errors)
    _validate_docs_text(root, errors)

    return {
        "schema_version": "scout_schema_validation_report.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "seed_count": len(seed_ids),
        "seed_ids": sorted(seed_ids),
        "required_relation_type_count": len(REQUIRED_RELATION_TYPES),
        "required_contract_count": len(REQUIRED_CONTRACTS),
        "required_policy_count": len(REQUIRED_POLICIES),
        "required_matrix_count": len(REQUIRED_MATRICES),
        "errors": errors,
    }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "scout_outputs_are_candidates",
        "scout_outputs_are_not_truth",
        "scout_does_not_create_evidence",
        "scout_does_not_create_reviewed_records",
        "scout_does_not_mutate_indexes",
        "scout_may_seed_search_needs",
        "scout_may_seed_workunits",
        "scout_may_create_discovery_trails",
        "scout_may_create_source_trust_observations",
        "scout_may_recommend_related_paths",
        "future_ai_outputs_candidate_only",
        "engagement_optimization_forbidden",
    )
    required_false = (
        "live_source_calls_enabled",
        "crawling_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "public_fanout_enabled",
        "master_index_mutation_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for flag in required_true:
        if policy.get(flag) is not True:
            errors.append(f"control/policies/scout_schema_policy.json: {flag} must be true.")
    for flag in required_false:
        if policy.get(flag) is not False:
            errors.append(f"control/policies/scout_schema_policy.json: {flag} must be false.")


def _validate_non_claim_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for flag in (
        "fake_evidence_created",
        "fake_verified_records_created",
        "live_source_call_performed",
        "source_probe_executed",
        "crawling_performed",
        "operator_instance_mutated",
        "master_index_mutated",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(flag) is not False:
            errors.append(f"control/policies/scout_non_claim_policy.json: {flag} must be false.")


def _validate_relation_matrix(matrix: Mapping[str, Any], errors: list[str]) -> None:
    relations = matrix.get("relation_types")
    if not isinstance(relations, list):
        errors.append("control/inventory/scout_relation_type_matrix.json: relation_types must be a list.")
        return
    ids = {str(item.get("relation_type", "")) for item in relations if isinstance(item, Mapping)}
    missing = set(REQUIRED_RELATION_TYPES) - ids
    if missing:
        errors.append(f"control/inventory/scout_relation_type_matrix.json: missing relation types {sorted(missing)}.")
    for item in relations:
        if not isinstance(item, Mapping):
            continue
        relation_type = str(item.get("relation_type", ""))
        for field in (
            "description",
            "allowed_domains",
            "evidence_required",
            "risk",
            "may_seed_workunit",
            "may_affect_source_trust_later",
            "public_safe_by_default",
        ):
            if field not in item:
                errors.append(f"{relation_type}: missing relation matrix field {field}.")
        if item.get("evidence_required") is not True:
            errors.append(f"{relation_type}: evidence_required must be true.")


def _validate_matrix_values(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    feedback = payloads.get("control/inventory/scout_feedback_event_matrix.json", {})
    feedback_ids = {
        str(item.get("event_type", ""))
        for item in _list(feedback.get("feedback_event_types"))
        if isinstance(item, Mapping)
    }
    missing_feedback = set(REQUIRED_FEEDBACK_EVENT_TYPES) - feedback_ids
    if missing_feedback:
        errors.append(f"control/inventory/scout_feedback_event_matrix.json: missing feedback events {sorted(missing_feedback)}.")

    workunits = payloads.get("control/inventory/scout_workunit_seed_matrix.json", {})
    workunit_ids = {
        str(item.get("suggestion_type", ""))
        for item in _list(workunits.get("workunit_seed_suggestion_types"))
        if isinstance(item, Mapping)
    }
    missing_workunits = set(REQUIRED_WORKUNIT_SEED_TYPES) - workunit_ids
    if missing_workunits:
        errors.append(f"control/inventory/scout_workunit_seed_matrix.json: missing WorkUnit seed types {sorted(missing_workunits)}.")

    console = payloads.get("control/inventory/scout_workbench_console_matrix.json", {})
    if set(_string_list(console.get("routes"))) != {"/scout", "/scout/trails", "/scout/sources", "/scout/candidates", "/scout/trust", "/scout/feedback"}:
        errors.append("control/inventory/scout_workbench_console_matrix.json: routes are incomplete.")


def _validate_example_record(record: Mapping[str, Any], schema_version: str, record_type: str, errors: list[str]) -> None:
    label = str(record.get("record_id") or record.get("related_path_id") or record.get("observation_id") or record.get("event_id") or record.get("workunit_seed_id") or record_type)
    if record.get("schema_version") != schema_version:
        errors.append(f"{label}: schema_version must be {schema_version}.")
    if record.get("record_type") != record_type:
        errors.append(f"{label}: record_type must be {record_type}.")
    if record.get("accepted_truth") is not False:
        errors.append(f"{label}: accepted_truth must be false.")
    if record.get("review_required") is not True:
        errors.append(f"{label}: review_required must be true.")
    non_claims = _mapping(record.get("non_claims"))
    for flag in ("evidence_created", "reviewed_record_created", "index_mutated", "live_source_call_performed", "crawling_performed"):
        if non_claims.get(flag) is not False:
            errors.append(f"{label}: non_claims.{flag} must be false.")


def _validate_handoffs(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    domain = payloads.get("control/inventory/scout_domain_handoff_matrix.json", {})
    domains = {
        str(item.get("domain_id", ""))
        for item in _list(domain.get("domains"))
        if isinstance(item, Mapping)
    }
    missing_domains = set(REQUIRED_DOMAIN_IDS) - domains
    if missing_domains:
        errors.append(f"control/inventory/scout_domain_handoff_matrix.json: missing domains {sorted(missing_domains)}.")
    syn = payloads.get("control/inventory/scout_syn_handoff_matrix.json", {})
    if not _list(syn.get("syn_cases")):
        errors.append("control/inventory/scout_syn_handoff_matrix.json: syn_cases must not be empty.")
    if _mapping(syn.get("non_claims")).get("fake_evidence_created") is not False:
        errors.append("control/inventory/scout_syn_handoff_matrix.json: must not create fake evidence.")


def _validate_docs_text(root: Path, errors: list[str]) -> None:
    for rel_path in REQUIRED_DOCS:
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in ("not truth", "no live source", "no crawling", "review"):
            if phrase not in text:
                errors.append(f"{rel_path}: must state {phrase!r}.")
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(f"{rel_path}: forbidden claim text {forbidden!r}.")


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"{path.relative_to(REPO_ROOT)}: required JSON file is missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)}: invalid JSON: {exc}.")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"{path.relative_to(REPO_ROOT)}: JSON root must be an object.")
        return {}
    return payload


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


if __name__ == "__main__":
    raise SystemExit(main())
