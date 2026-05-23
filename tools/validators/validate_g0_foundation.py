#!/usr/bin/env python3
"""Validate G0 ranking/explanation/identity/user-cost foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval.g0_quality import (  # noqa: E402
    BLOCKED_ACTIONS,
    PROJECTION_PROFILES,
    REQUIRED_EXPLANATION_FACTORS,
    REQUIRED_IDENTITY_GROUP_TYPES,
    REQUIRED_SCORE_SIGNALS,
    REQUIRED_USER_COST_CLASSES,
    build_explanation_packet,
    build_identity_cluster_candidates,
    build_near_miss_candidates,
    build_quality_console_view,
    build_score_breakdown,
    build_user_cost_score,
    load_quality_fixture,
    validate_score_signal,
)


TASK = "AIDE-BATCH-G0-QUALITY-FOUNDATION-01"
FIXTURE_PATH = "examples/search/quality/sample_quality_fixture.json"

REQUIRED_POLICIES = (
    "control/policies/g0_ranking_policy.json",
    "control/policies/g0_explanation_policy.json",
    "control/policies/g0_identity_policy.json",
    "control/policies/g0_user_cost_policy.json",
    "control/policies/g0_non_claim_policy.json",
    "control/policies/g0_future_ai_policy.json",
)

REQUIRED_CONTRACTS = (
    "contracts/search/quality/README.md",
    "contracts/search/quality/score_signal.v0.json",
    "contracts/search/quality/score_breakdown.v0.json",
    "contracts/search/quality/result_quality_report.v0.json",
    "contracts/search/quality/query_fit_signal.v0.json",
    "contracts/search/quality/domain_fit_signal.v0.json",
    "contracts/search/quality/source_quality_signal.v0.json",
    "contracts/search/quality/provenance_signal.v0.json",
    "contracts/explanation/README.md",
    "contracts/explanation/explanation_packet.v0.json",
    "contracts/explanation/explanation_factor.v0.json",
    "contracts/explanation/blocked_action_explanation.v0.json",
    "contracts/explanation/uncertainty_explanation.v0.json",
    "contracts/explanation/absence_explanation.v0.json",
    "contracts/identity/README.md",
    "contracts/identity/identity_cluster_candidate.v0.json",
    "contracts/identity/duplicate_candidate.v0.json",
    "contracts/identity/near_miss_candidate.v0.json",
    "contracts/identity/representation_group.v0.json",
    "contracts/user_cost/README.md",
    "contracts/user_cost/user_cost_score.v0.json",
    "contracts/user_cost/actionability_score.v0.json",
    "contracts/user_cost/manual_burden_estimate.v0.json",
    "contracts/user_cost/result_effort_class.v0.json",
)

REQUIRED_MATRICES = (
    "control/inventory/g0_contract_matrix.json",
    "control/inventory/g0_score_signal_matrix.json",
    "control/inventory/g0_explanation_packet_matrix.json",
    "control/inventory/g0_identity_cluster_matrix.json",
    "control/inventory/g0_near_miss_matrix.json",
    "control/inventory/g0_user_cost_matrix.json",
    "control/inventory/g0_actionability_matrix.json",
    "control/inventory/g0_domain_handoff_matrix.json",
    "control/inventory/g0_scout_handoff_matrix.json",
    "control/inventory/g0_syn_handoff_matrix.json",
    "control/inventory/g0_f0_handoff_matrix.json",
    "control/inventory/g0_workbench_console_matrix.json",
)

REQUIRED_DOCS = (
    "docs/architecture/G0_RANKING_EXPLANATION_QUALITY.md",
    "docs/architecture/G0_IDENTITY_AND_NEAR_MISS_MODEL.md",
    "docs/architecture/G0_USER_COST_AND_ACTIONABILITY.md",
    "docs/operations/G0_FOUNDATION_RUNBOOK.md",
    "docs/operations/POST_G0_FOUNDATION_PLAN.md",
    "docs/reference/G0_SCORE_SIGNAL.md",
    "docs/reference/G0_EXPLANATION_PACKET.md",
    "docs/reference/G0_IDENTITY_CLUSTER.md",
    "docs/reference/G0_USER_COST_SCORE.md",
    "docs/reference/G0_BLOCKED_CLAIMS.md",
)

REQUIRED_SCRIPTS = (
    "scripts/eureka_g0_score.py",
    "scripts/eureka_g0_explain.py",
    "scripts/eureka_g0_identity.py",
    "scripts/eureka_g0_user_cost.py",
    "scripts/eureka_g0_console.py",
    "scripts/eureka_g0_smoke.py",
    "scripts/validate_g0_foundation.py",
)

REQUIRED_EXAMPLES = (
    "examples/search/quality/sample_score_signal.json",
    "examples/search/quality/sample_score_breakdown.json",
    "examples/search/quality/sample_explanation_packet.json",
    "examples/search/quality/sample_identity_cluster_candidate.json",
    "examples/search/quality/sample_near_miss_candidate.json",
    "examples/search/quality/sample_user_cost_score.json",
    "examples/search/quality/sample_quality_console_view.json",
    "examples/search/quality/sample_quality_fixture.json",
)

FORBIDDEN_TEXT = (
    "production-ready",
    "public launch ready",
    "accepted evidence truth",
    "verified record created",
    "accepted identity merge created",
    "model call completed",
    "live source call completed",
    "source probe completed",
    "download completed",
    "extraction completed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate_g0_foundation(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("G0 quality foundation validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_g0_foundation(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for rel_path in (*REQUIRED_CONTRACTS, *REQUIRED_DOCS, *REQUIRED_SCRIPTS, *REQUIRED_EXAMPLES):
        if not (root / rel_path).is_file():
            errors.append(f"{rel_path}: required file is missing.")

    for rel_path in (*REQUIRED_POLICIES, *REQUIRED_MATRICES):
        payload = _load_json(root / rel_path, errors)
        if isinstance(payload, Mapping):
            payloads[rel_path] = payload

    _validate_policy(payloads.get("control/policies/g0_ranking_policy.json", {}), errors)
    _validate_non_claim_policy(payloads.get("control/policies/g0_non_claim_policy.json", {}), errors)
    _validate_score_signal_matrix(payloads.get("control/inventory/g0_score_signal_matrix.json", {}), errors)
    _validate_explanation_matrix(payloads.get("control/inventory/g0_explanation_packet_matrix.json", {}), errors)
    _validate_identity_matrices(payloads, errors)
    _validate_user_cost_matrices(payloads, errors)
    _validate_handoffs(payloads, errors)

    fixture = load_quality_fixture(root / FIXTURE_PATH)
    if fixture.get("schema_version") != "g0_quality_fixture.v0":
        errors.append(f"{FIXTURE_PATH}: schema_version must be g0_quality_fixture.v0.")
    if _mapping(fixture.get("non_claims")).get("fake_evidence_created") is not False:
        errors.append(f"{FIXTURE_PATH}: fixture must not create fake evidence.")
    records = [record for record in fixture.get("records", []) if isinstance(record, Mapping)]
    if len(records) < 8:
        errors.append(f"{FIXTURE_PATH}: must include at least eight G0 fixture result cases.")

    score_breakdowns = [build_score_breakdown(record, fixture.get("query_context", {}), fixture.get("domain_context", {})) for record in records]
    if not score_breakdowns:
        errors.append("G0 score decomposition must produce at least one score breakdown.")
    for score in score_breakdowns:
        if not score.get("signals"):
            errors.append(f"{score.get('result_ref')}: score breakdown must include signals.")
        if score.get("accepted_truth") is not False:
            errors.append(f"{score.get('result_ref')}: score breakdown must not accept truth.")
        for signal in score.get("signals", []):
            if isinstance(signal, Mapping):
                errors.extend(validate_score_signal(signal)["errors"])

    explanations = [build_explanation_packet(score, record) for score, record in zip(score_breakdowns, records)]
    for explanation in explanations:
        for field in (
            "why_result_appeared",
            "why_result_ranked_here",
            "why_result_is_limited",
            "why_actions_are_blocked",
            "what_would_improve_confidence",
            "what_remaining_work_exists",
            "uncertainty",
            "limitations",
        ):
            if not explanation.get(field):
                errors.append(f"{explanation.get('result_ref')}: explanation missing {field}.")
        if explanation.get("accepted_truth") is not False:
            errors.append(f"{explanation.get('result_ref')}: explanation must not accept truth.")

    identity = build_identity_cluster_candidates(records)
    if not identity.get("identity_cluster_candidates"):
        errors.append("G0 identity cluster candidates must include at least one provisional cluster.")
    for cluster in identity.get("identity_cluster_candidates", []):
        if isinstance(cluster, Mapping) and cluster.get("accepted_identity_merge") is not False:
            errors.append(f"{cluster.get('identity_cluster_id')}: accepted_identity_merge must be false.")

    near_misses = build_near_miss_candidates(records, fixture.get("query_context", {}))
    if not near_misses.get("near_miss_candidates"):
        errors.append("G0 near-miss candidates must include at least one mismatch explanation.")

    user_costs = [build_user_cost_score(record, fixture.get("action_posture", {})) for record in records]
    if not user_costs:
        errors.append("G0 user-cost scoring must produce at least one score.")
    for cost in user_costs:
        if not cost.get("user_cost_class"):
            errors.append(f"{cost.get('result_ref')}: user cost class is required.")
        if cost.get("accepted_truth") is not False:
            errors.append(f"{cost.get('result_ref')}: user cost score must not accept truth.")

    for profile in PROJECTION_PROFILES:
        view = build_quality_console_view(fixture, profile)
        if view.get("read_only") is not True:
            errors.append(f"{profile}: quality console must be read-only.")
        if set(view.get("blocked_actions", [])) != set(BLOCKED_ACTIONS):
            errors.append(f"{profile}: quality console must carry all blocked actions.")
        if _mapping(view.get("non_claims")).get("model_provider_used") is not False:
            errors.append(f"{profile}: quality console must not use model providers.")

    _validate_script_smoke(root, errors)
    _validate_docs_text(root, errors)

    return {
        "schema_version": "g0_foundation_validation_report.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "required_contract_count": len(REQUIRED_CONTRACTS),
        "required_policy_count": len(REQUIRED_POLICIES),
        "required_matrix_count": len(REQUIRED_MATRICES),
        "fixture_result_count": len(records),
        "score_breakdown_count": len(score_breakdowns),
        "explanation_packet_count": len(explanations),
        "identity_cluster_candidate_count": len(identity.get("identity_cluster_candidates", [])),
        "near_miss_candidate_count": len(near_misses.get("near_miss_candidates", [])),
        "errors": errors,
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "accepted_identity_merge_created": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "ranking_does_not_create_truth",
        "score_is_not_evidence",
        "explanation_is_not_evidence",
        "identity_cluster_is_provisional_by_default",
        "future_ai_outputs_candidate_only",
        "score_decomposition_required",
        "explanation_required_for_scored_results",
        "uncertainty_required",
        "limitations_required",
        "blocked_action_explanation_required",
    )
    required_false = (
        "accepted_identity_merge_enabled",
        "reviewed_record_creation_enabled",
        "master_index_mutation_enabled",
        "public_ranking_claim_enabled",
        "live_source_calls_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for flag in required_true:
        if policy.get(flag) is not True:
            errors.append(f"control/policies/g0_ranking_policy.json: {flag} must be true.")
    for flag in required_false:
        if policy.get(flag) is not False:
            errors.append(f"control/policies/g0_ranking_policy.json: {flag} must be false.")


def _validate_non_claim_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for flag in (
        "fake_evidence_created",
        "fake_verified_records_created",
        "accepted_identity_merge_created",
        "live_source_call_performed",
        "source_probe_executed",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "operator_instance_mutated",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(flag) is not False:
            errors.append(f"control/policies/g0_non_claim_policy.json: {flag} must be false.")


def _validate_score_signal_matrix(matrix: Mapping[str, Any], errors: list[str]) -> None:
    ids = {str(item.get("signal_id", "")) for item in _list(matrix.get("score_signals")) if isinstance(item, Mapping)}
    missing = set(REQUIRED_SCORE_SIGNALS) - ids
    if missing:
        errors.append(f"control/inventory/g0_score_signal_matrix.json: missing score signals {sorted(missing)}.")


def _validate_explanation_matrix(matrix: Mapping[str, Any], errors: list[str]) -> None:
    ids = {str(item.get("factor_type", "")) for item in _list(matrix.get("explanation_factor_types")) if isinstance(item, Mapping)}
    missing = set(REQUIRED_EXPLANATION_FACTORS) - ids
    if missing:
        errors.append(f"control/inventory/g0_explanation_packet_matrix.json: missing explanation factors {sorted(missing)}.")
    for field in (
        "why_result_appeared",
        "why_result_ranked_here",
        "why_result_is_limited",
        "why_actions_are_blocked",
        "what_would_improve_confidence",
        "what_remaining_work_exists",
    ):
        if field not in _list(matrix.get("required_packet_sections")):
            errors.append(f"control/inventory/g0_explanation_packet_matrix.json: missing required section {field}.")


def _validate_identity_matrices(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    matrix = payloads.get("control/inventory/g0_identity_cluster_matrix.json", {})
    group_types = {str(item.get("group_type", "")) for item in _list(matrix.get("candidate_group_types")) if isinstance(item, Mapping)}
    missing = set(REQUIRED_IDENTITY_GROUP_TYPES) - group_types
    if missing:
        errors.append(f"control/inventory/g0_identity_cluster_matrix.json: missing group types {sorted(missing)}.")
    if matrix.get("accepted_identity_merge_enabled") is not False:
        errors.append("control/inventory/g0_identity_cluster_matrix.json: accepted_identity_merge_enabled must be false.")
    near = payloads.get("control/inventory/g0_near_miss_matrix.json", {})
    if near.get("near_misses_explain_mismatch") is not True:
        errors.append("control/inventory/g0_near_miss_matrix.json: near_misses_explain_mismatch must be true.")


def _validate_user_cost_matrices(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    matrix = payloads.get("control/inventory/g0_user_cost_matrix.json", {})
    classes = {str(item.get("user_cost_class", "")) for item in _list(matrix.get("user_cost_classes")) if isinstance(item, Mapping)}
    missing = set(REQUIRED_USER_COST_CLASSES) - classes
    if missing:
        errors.append(f"control/inventory/g0_user_cost_matrix.json: missing user-cost classes {sorted(missing)}.")
    actionability = payloads.get("control/inventory/g0_actionability_matrix.json", {})
    if not _list(actionability.get("actionability_levels")):
        errors.append("control/inventory/g0_actionability_matrix.json: actionability_levels are required.")


def _validate_handoffs(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    for rel_path, key in (
        ("control/inventory/g0_domain_handoff_matrix.json", "domain_handoffs"),
        ("control/inventory/g0_scout_handoff_matrix.json", "scout_handoffs"),
        ("control/inventory/g0_syn_handoff_matrix.json", "syn_handoffs"),
        ("control/inventory/g0_f0_handoff_matrix.json", "f0_handoffs"),
        ("control/inventory/g0_workbench_console_matrix.json", "views"),
    ):
        payload = payloads.get(rel_path, {})
        if not _list(payload.get(key)):
            errors.append(f"{rel_path}: {key} must not be empty.")


def _validate_script_smoke(root: Path, errors: list[str]) -> None:
    commands = (
        ("scripts/eureka_g0_score.py", "--fixture", FIXTURE_PATH, "--json"),
        ("scripts/eureka_g0_explain.py", "--fixture", FIXTURE_PATH, "--json"),
        ("scripts/eureka_g0_identity.py", "--fixture", FIXTURE_PATH, "--json"),
        ("scripts/eureka_g0_user_cost.py", "--fixture", FIXTURE_PATH, "--json"),
        ("scripts/eureka_g0_smoke.py", "--fixture", FIXTURE_PATH, "--projection", "operator_workbench", "--json"),
    )
    for command in commands:
        completed = subprocess.run([sys.executable, *command], cwd=root, capture_output=True, text=True)
        if completed.returncode != 0:
            errors.append(f"{' '.join(command)} failed: {completed.stderr.strip() or completed.stdout.strip()}")


def _validate_docs_text(root: Path, errors: list[str]) -> None:
    for rel_path in (*REQUIRED_DOCS, *REQUIRED_CONTRACTS):
        path = root / rel_path
        if not path.exists() or path.suffix.lower() == ".json":
            continue
        text = path.read_text(encoding="utf-8").lower()
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(f"{rel_path}: forbidden claim text {forbidden!r}.")


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"{_rel(path)}: required JSON file is missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}")
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


if __name__ == "__main__":
    raise SystemExit(main())
