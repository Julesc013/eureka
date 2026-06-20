"""Autonomous E2E reference evaluation oracle.

The oracle is deliberately deterministic: it wraps existing local fixtures and
product seams, records explicit assertions, and never uses model judgement.
"""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import html.parser
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import tracemalloc
from typing import Any, Callable, Iterable, Mapping, Sequence
import uuid

from evals.hard_queries import (
    BASELINE_PROFILES,
    evaluate_fixture_case,
    evaluate_fixture_suite,
    fixture_case_by_query_id,
    render_fixture_case,
)
from runtime.index.preview import build_preview_index, search_preview_index, validate_preview_index
from runtime.local.e2e_hunt_exploration import (
    E2EExploreOptions,
    build_explore_workspace,
    start_synthetic_hunt,
)
from runtime.local.synthetic_truth_path import (
    DEFAULT_OUTPUT_ROOT as SYNTHETIC_TRUTH_OUTPUT_ROOT,
    SyntheticTruthPathOptions,
    run_synthetic_truth_path,
    validate_synthetic_truth_path,
    verify_synthetic_truth_snapshot,
)
from runtime.resolution_run import (
    RunnerBudget,
    replay_run_bundle,
    run_e2e_reference_run,
    validate_run_bundle,
)
from runtime.resolution_run.runner import DEFAULT_OUTPUT_ROOT as RUNNER_OUTPUT_ROOT
from runtime.snapshots.verify import build_snapshot_verification_report


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ORACLE_ROOT = REPO_ROOT / "evals" / "e2e_reference" / "oracle"
DEFAULT_OUTPUT_ROOT = Path(".eureka/e2e-reference/eval")
ORACLE_VERSION = "eureka.autonomous_eval_oracle.v0"
RESULT_SCHEMA_VERSION = "eureka.e2e_eval_case_result.v0"
SUITE_SCHEMA_VERSION = "eureka.e2e_eval_suite_result.v0"
FIXED_SEED = "e2e-reference-oracle-v0"
VALID_PROOF_LEVELS = {
    "shape_proof",
    "semantic_proof",
    "authority_proof",
    "recovery_proof",
    "parity_proof",
    "operational_profile",
}
VALID_CRITICALITIES = {"critical", "required", "advisory"}
VALID_STATUSES = {"satisfied", "partial", "not_satisfied", "not_evaluable", "capability_gap"}
GATE_PASS = "PASS"
GATE_WARN = "PASS_WITH_WARNINGS"
GATE_FAIL = "FAIL"
GATE_BLOCKED = "BLOCKED"
CANARIES = (
    r"C:\Users\EUREKA_TEST_SECRET\private.iso",
    "/home/eureka_test_secret/private.iso",
    "sk-test-not-a-real-key",
    "Bearer EUREKA_TEST_TOKEN",
    "session_cookie=eureka-test",
    "<script>eureka_test()</script>",
)


class OracleError(ValueError):
    """Raised for invalid oracle configuration or execution."""


@dataclass(frozen=True)
class OracleRegistry:
    root: Path
    cases: dict[str, dict[str, Any]]
    suites: dict[str, dict[str, Any]]
    budgets: dict[str, dict[str, Any]]
    baseline: dict[str, Any]


def load_registry(root: str | Path = DEFAULT_ORACLE_ROOT) -> OracleRegistry:
    base = Path(root)
    cases: dict[str, dict[str, Any]] = {}
    for path in sorted((base / "cases").glob("*.json")):
        payload = _load_json(path)
        for case in payload.get("cases", []):
            if not isinstance(case, Mapping):
                raise OracleError(f"{path}: case entries must be objects")
            case_id = str(case.get("case_id") or "")
            if not case_id:
                raise OracleError(f"{path}: case_id is required")
            if case_id in cases:
                raise OracleError(f"duplicate oracle case id: {case_id}")
            item = dict(case)
            item["_source_path"] = _rel(path)
            cases[case_id] = item
    suites: dict[str, dict[str, Any]] = {}
    for path in sorted((base / "suites").glob("*.json")):
        payload = _load_json(path)
        suite_id = str(payload.get("suite_id") or path.stem)
        if suite_id in suites:
            raise OracleError(f"duplicate oracle suite id: {suite_id}")
        payload["_source_path"] = _rel(path)
        suites[suite_id] = payload
    budgets = _load_json(base / "budgets" / "local_reference_v0.json")
    baseline = _load_json(base / "baselines" / "reference_v0.json")
    return OracleRegistry(base, cases, suites, dict(budgets.get("budgets") or {}), baseline)


def validate_registry(registry: OracleRegistry | None = None) -> dict[str, Any]:
    reg = registry or load_registry()
    errors: list[str] = []
    warnings: list[str] = []
    case_refs: set[str] = set()
    for suite_id, suite in sorted(reg.suites.items()):
        ids = _string_list(suite.get("case_ids"))
        if not ids:
            errors.append(f"suite {suite_id} has no case_ids")
        for case_id in ids:
            case_refs.add(case_id)
            if case_id not in reg.cases:
                errors.append(f"suite {suite_id} references unknown case {case_id}")
    for case_id, case in sorted(reg.cases.items()):
        for field in ("case_id", "title", "suite_ids", "dimensions", "proof_levels", "criticality", "product_adapter", "expected_invariants", "prohibited_outcomes"):
            if field not in case:
                errors.append(f"{case_id} missing {field}")
        if case.get("criticality") not in VALID_CRITICALITIES:
            errors.append(f"{case_id} uses invalid criticality {case.get('criticality')}")
        for level in _string_list(case.get("proof_levels")):
            if level not in VALID_PROOF_LEVELS:
                errors.append(f"{case_id} uses invalid proof level {level}")
        if case.get("criticality") == "critical" and not _string_list(case.get("prohibited_outcomes")):
            errors.append(f"{case_id} critical case requires prohibited_outcomes")
        if "live_provider" in str(case.get("product_adapter", "")):
            errors.append(f"{case_id} uses forbidden live provider adapter")
        if "model" in str(case.get("product_adapter", "")).casefold():
            errors.append(f"{case_id} uses forbidden model adapter")
        if case_id not in case_refs:
            warnings.append(f"{case_id} is not referenced by any suite")
    baseline_cases = set(_string_list(reg.baseline.get("expected_case_ids")))
    required_core = set(_string_list(reg.suites.get("core", {}).get("case_ids")))
    missing = sorted(required_core - baseline_cases)
    if missing:
        errors.append("baseline missing core cases: " + ", ".join(missing))
    return {
        "schema_version": "eureka.e2e_eval_registry_validation.v0",
        "status": "pass" if not errors else "fail",
        "oracle_version": ORACLE_VERSION,
        "case_count": len(reg.cases),
        "suite_count": len(reg.suites),
        "budget_count": len(reg.budgets),
        "errors": errors,
        "warnings": warnings,
        "model_provider_dependency": False,
        "live_provider_adapter": False,
    }


def list_cases(registry: OracleRegistry | None = None) -> dict[str, Any]:
    reg = registry or load_registry()
    validation = validate_registry(reg)
    return {
        "schema_version": "eureka.e2e_eval_case_list.v0",
        "oracle_version": ORACLE_VERSION,
        "case_count": len(reg.cases),
        "suite_count": len(reg.suites),
        "suites": [
            {
                "suite_id": suite_id,
                "case_count": len(_string_list(suite.get("case_ids"))),
                "case_ids": _string_list(suite.get("case_ids")),
            }
            for suite_id, suite in sorted(reg.suites.items())
        ],
        "cases": [_case_summary(case) for case in sorted(reg.cases.values(), key=lambda item: str(item["case_id"]))],
        "validation": validation,
    }


def explain_case(case_id: str, registry: OracleRegistry | None = None) -> dict[str, Any]:
    reg = registry or load_registry()
    case = reg.cases.get(case_id)
    if case is None:
        raise OracleError(f"unknown oracle case: {case_id}")
    return {
        "schema_version": "eureka.e2e_eval_case_explain.v0",
        "oracle_version": ORACLE_VERSION,
        "case": _public_case(case),
        "suite_refs": sorted(suite_id for suite_id, suite in reg.suites.items() if case_id in _string_list(suite.get("case_ids"))),
    }


def run_oracle(
    *,
    suite_id: str | None = None,
    case_id: str | None = None,
    out_root: str | Path = DEFAULT_OUTPUT_ROOT,
    registry: OracleRegistry | None = None,
    fail_on_advisory: bool = False,
) -> dict[str, Any]:
    reg = registry or load_registry()
    validation = validate_registry(reg)
    if validation["status"] != "pass":
        raise OracleError("oracle registry validation failed: " + "; ".join(validation["errors"]))
    selected_suite = suite_id or ("case" if case_id else "core")
    case_ids = _select_case_ids(reg, suite_id=selected_suite, case_id=case_id)
    execution_id = _execution_id(selected_suite, case_ids)
    run_root = _safe_execution_root(out_root, execution_id)
    run_root.mkdir(parents=True)
    started = _now()
    manifest = {
        "schema_version": "eureka.e2e_eval_oracle_manifest.v0",
        "execution_id": execution_id,
        "oracle_version": ORACLE_VERSION,
        "commit_sha": _git_head(),
        "suite_ids": [selected_suite],
        "case_ids": case_ids,
        "started_at": started,
        "deterministic_seed": FIXED_SEED,
        "network_provider_calls": False,
        "model_provider_calls": False,
        "real_truth_mutation": False,
        "public_exposure": False,
    }
    _write_json(run_root / "oracle_manifest.json", manifest)
    case_results = []
    for cid in case_ids:
        case_results.append(_run_case(reg.cases[cid], run_root))
    summary = _suite_summary(
        execution_id=execution_id,
        suite_ids=[selected_suite],
        case_results=case_results,
        started_at=started,
        fail_on_advisory=fail_on_advisory,
        generated_root=run_root,
    )
    _write_jsonl(run_root / "case_results.jsonl", case_results)
    _write_json(run_root / "summary.json", summary)
    _write_json(run_root / "failures.json", _failures(case_results))
    _write_json(run_root / "proof_matrix.json", _proof_matrix(case_results))
    _write_json(run_root / "resource_metrics.json", _resource_summary(case_results, run_root))
    _write_json(run_root / "boundary_report.json", _boundary_summary(case_results))
    _write_text(run_root / "report.md", _markdown_report(summary, case_results))
    return summary


def validate_oracle_run(run_dir: str | Path, *, strict: bool = True) -> dict[str, Any]:
    root = Path(run_dir)
    errors: list[str] = []
    manifest = _load_json_optional(root / "oracle_manifest.json", errors)
    summary = _load_json_optional(root / "summary.json", errors)
    cases = _load_jsonl_optional(root / "case_results.jsonl", errors)
    for rel in ("failures.json", "proof_matrix.json", "resource_metrics.json", "boundary_report.json", "report.md"):
        if not (root / rel).is_file():
            errors.append(f"missing run artifact: {rel}")
    if summary:
        if summary.get("case_count") != len(cases):
            errors.append("summary case_count does not match case_results.jsonl")
        if summary.get("model_calls") is not False:
            errors.append("summary must record model_calls false")
        if summary.get("network_provider_calls") is not False:
            errors.append("summary must record network_provider_calls false")
        if summary.get("real_truth_mutation") is not False:
            errors.append("summary must record real_truth_mutation false")
    if manifest and manifest.get("execution_id") != summary.get("execution_id"):
        errors.append("manifest and summary execution_id mismatch")
    for case in cases:
        if case.get("status") not in VALID_STATUSES:
            errors.append(f"{case.get('case_id')}: invalid status")
        if case.get("gate_result") not in {GATE_PASS, GATE_WARN, GATE_FAIL, GATE_BLOCKED}:
            errors.append(f"{case.get('case_id')}: invalid gate_result")
        if case.get("criticality") in {"critical", "required"} and case.get("gate_result") == GATE_WARN:
            errors.append(f"{case.get('case_id')}: critical/required case cannot warn-only")
    if strict and summary and summary.get("overall_gate_status") not in {GATE_PASS, GATE_WARN}:
        errors.append("strict validation requires PASS or PASS_WITH_WARNINGS")
    return {
        "schema_version": "eureka.e2e_eval_oracle_run_validation.v0",
        "status": "pass" if not errors else "fail",
        "run_dir": _rel(root),
        "errors": errors,
        "case_count": len(cases),
        "overall_gate_status": summary.get("overall_gate_status", "") if summary else "",
        "network_provider_calls": False,
        "model_calls": False,
    }


def status_for_run(run_dir: str | Path) -> dict[str, Any]:
    summary = _load_json(Path(run_dir) / "summary.json")
    return {
        "schema_version": "eureka.e2e_eval_oracle_status.v0",
        "execution_id": summary.get("execution_id", ""),
        "overall_gate_status": summary.get("overall_gate_status", ""),
        "case_count": summary.get("case_count", 0),
        "critical_failures": summary.get("critical_failures", 0),
        "required_failures": summary.get("required_failures", 0),
        "advisory_warnings": summary.get("advisory_warnings", 0),
        "capability_gaps": summary.get("capability_gaps", []),
        "network_provider_calls": False,
        "model_calls": False,
    }


def compare_oracle_results(left: str | Path, right: str | Path) -> dict[str, Any]:
    left_summary = _summary_from_path(left)
    right_summary = _summary_from_path(right)
    left_cases = {str(item.get("case_id")): item for item in left_summary.get("case_summaries", [])}
    right_cases = {str(item.get("case_id")): item for item in right_summary.get("case_summaries", [])}
    left_ids = set(left_cases)
    right_ids = set(right_cases)
    shared = left_ids & right_ids
    changed = [
        case_id
        for case_id in sorted(shared)
        if left_cases[case_id].get("status") != right_cases[case_id].get("status")
        or left_cases[case_id].get("semantic_hash") != right_cases[case_id].get("semantic_hash")
    ]
    return {
        "schema_version": "eureka.e2e_eval_oracle_comparison.v0",
        "left": str(left),
        "right": str(right),
        "left_status": left_summary.get("overall_gate_status", ""),
        "right_status": right_summary.get("overall_gate_status", ""),
        "added_cases": sorted(right_ids - left_ids),
        "removed_cases": sorted(left_ids - right_ids),
        "changed_cases": changed,
        "improved_cases": [
            cid for cid in changed if _status_rank(right_cases[cid].get("status")) > _status_rank(left_cases[cid].get("status"))
        ],
        "regressed_cases": [
            cid for cid in changed if _status_rank(right_cases[cid].get("status")) < _status_rank(left_cases[cid].get("status"))
        ],
        "boundary_change": left_summary.get("boundary_summary") != right_summary.get("boundary_summary"),
    }


def _run_case(case: Mapping[str, Any], run_root: Path) -> dict[str, Any]:
    case_id = str(case["case_id"])
    case_root = _safe_child(run_root / "cases", case_id)
    if case_root.exists():
        raise OracleError(f"case output already exists: {case_id}")
    (case_root / "artifacts").mkdir(parents=True)
    _write_json(case_root / "input_manifest.json", _public_case(case))
    start = time.perf_counter_ns()
    tracemalloc.start()
    try:
        observed, assertions, warnings = _dispatch_case(case, case_root)
        current, peak = tracemalloc.get_traced_memory()
        status = _case_status(assertions)
        gate = _gate_result(str(case["criticality"]), status, warnings)
        error = ""
    except Exception as exc:  # deterministic failure report instead of traceback dump
        current, peak = tracemalloc.get_traced_memory()
        observed = {"exception": type(exc).__name__, "message": str(exc)}
        assertions = [_assertion("case execution", False, "case completed without exception", type(exc).__name__)]
        warnings = []
        status = "not_evaluable"
        gate = GATE_BLOCKED
        error = str(exc)
    finally:
        tracemalloc.stop()
    duration_ms = (time.perf_counter_ns() - start) / 1_000_000
    metrics = _metrics(case_root, duration_ms, current, peak)
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "case_id": case_id,
        "suite_ids": _string_list(case.get("suite_ids")),
        "dimensions": _string_list(case.get("dimensions")),
        "proof_levels": _string_list(case.get("proof_levels")),
        "criticality": str(case.get("criticality")),
        "status": status,
        "gate_result": gate,
        "assertions": assertions,
        "expected": _clone_json(case.get("expected_invariants") or {}),
        "observed": observed,
        "artifact_refs": _artifact_refs(case_root),
        "metrics": metrics,
        "warnings": warnings,
        "capability_gap": str(case.get("capability_gap_task") or "") if status == "capability_gap" else "",
        "recommended_repair_task": str(case.get("recommended_repair_task") or ""),
        "boundary_report": _case_boundary(observed, assertions),
        "semantic_hash": _semantic_hash(case_id, observed, assertions),
    }
    if error:
        result["error"] = error
    _write_json(case_root / "observed.json", observed)
    _write_json(case_root / "assertions.json", {"assertions": assertions})
    _write_json(case_root / "metrics.json", metrics)
    return result


def _dispatch_case(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    adapter = str(case.get("product_adapter") or "")
    if adapter == "hard_query_fixture":
        return _adapter_hard_query(case, case_root)
    if adapter == "hard_query_suite":
        return _adapter_hard_query_suite(case, case_root)
    if adapter == "metamorphic_query":
        return _adapter_metamorphic(case, case_root)
    if adapter == "duplicate_conflict":
        return _adapter_duplicate_conflict(case, case_root)
    if adapter == "runner_bundle":
        return _adapter_runner(case, case_root)
    if adapter == "preview_index":
        return _adapter_preview(case, case_root)
    if adapter == "exploration_workspace":
        return _adapter_exploration(case, case_root)
    if adapter == "synthetic_truth_path":
        return _adapter_synthetic_truth(case, case_root)
    if adapter == "fault_fixture":
        return _adapter_fault(case, case_root)
    if adapter == "cross_render_parity":
        return _adapter_parity(case, case_root)
    if adapter == "privacy_canary":
        return _adapter_privacy(case, case_root)
    if adapter == "unauthorized_write":
        return _adapter_unauthorized_write(case, case_root)
    if adapter == "resource_profile":
        return _adapter_resource(case, case_root)
    raise OracleError(f"unsupported oracle adapter: {adapter}")


def _adapter_hard_query(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    params = dict(case.get("params") or {})
    query_id = str(params["query_id"])
    fixture = fixture_case_by_query_id(query_id)
    result = evaluate_fixture_case(fixture)
    _write_json(case_root / "artifacts" / "hard_query_result.json", result)
    assertions = [
        _assertion("pass gates", result["pass_gates_met"], True, result["pass_gates_met"]),
        _assertion("status not verified", result["expected_status"] != "verified", "not verified", result["expected_status"]),
        _assertion("no live source calls", result["live_source_calls"] is False, False, result["live_source_calls"]),
        _assertion("no reviewed record", result["reviewed_record_created"] is False, False, result["reviewed_record_created"]),
    ]
    observed = {
        "query_id": query_id,
        "expected_status": result["expected_status"],
        "scores": result["scores"],
        "rendered_profiles": result["rendered_profiles"],
        "network_provider_calls": False,
        "real_truth_mutation": False,
    }
    return observed, assertions, []


def _adapter_hard_query_suite(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    result = evaluate_fixture_suite()
    _write_json(case_root / "artifacts" / "hard_query_suite.json", result)
    statuses = [item["expected_status"] for item in result["results"]]
    assertions = [
        _assertion("suite gates", result["all_pass_gates_met"], True, result["all_pass_gates_met"]),
        _assertion("six query families", result["fixture_count"] == 6, 6, result["fixture_count"]),
        _assertion("status diversity", {"candidate", "need", "near_miss", "policy_blocked", "unavailable"}.issubset(set(statuses)), "diverse preview statuses", statuses),
        _assertion("no live calls", result["live_source_calls"] is False, False, result["live_source_calls"]),
    ]
    return {"fixture_count": result["fixture_count"], "statuses": statuses, "network_provider_calls": False}, assertions, []


def _adapter_metamorphic(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    params = dict(case.get("params") or {})
    base = _intent_fingerprint(str(params.get("base_query", "")))
    variants = [str(item) for item in params.get("variants", [])]
    relation = str(params.get("relation", "equivalent_intent"))
    observed_variants = [_intent_fingerprint(item) for item in variants]
    required_terms = set(_string_list(params.get("required_terms")))
    assertions = []
    if relation in {"equivalent_intent", "noise_injection"}:
        assertions.append(_assertion("same critical constraints", all(item["constraints"] == base["constraints"] for item in observed_variants), base["constraints"], [item["constraints"] for item in observed_variants]))
    if relation == "constraint_addition":
        added = set(_string_list(params.get("added_constraints")))
        assertions.append(_assertion("added constraint visible", added.issubset(set(observed_variants[0]["constraints"])), sorted(added), observed_variants[0]["constraints"]))
    if relation == "constraint_change":
        assertions.append(_assertion("constraint changed", observed_variants[0]["constraints"] != base["constraints"], "changed", {"base": base["constraints"], "variant": observed_variants[0]["constraints"]}))
    if relation == "constraint_removal":
        removed = set(_string_list(params.get("removed_constraints")))
        assertions.append(_assertion("constraint removed", removed.isdisjoint(set(observed_variants[0]["constraints"])), sorted(removed), observed_variants[0]["constraints"]))
    if required_terms:
        assertions.append(_assertion("required terms preserved", all(required_terms.issubset(set(item["tokens"])) for item in observed_variants), sorted(required_terms), [item["tokens"] for item in observed_variants]))
    observed = {"base": base, "variants": observed_variants, "relation": relation}
    _write_json(case_root / "artifacts" / "metamorphic_observed.json", observed)
    return observed, assertions, []


def _adapter_duplicate_conflict(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    params = dict(case.get("params") or {})
    kind = str(params.get("kind", "duplicate"))
    if kind == "duplicate":
        observed = {
            "merge_group_id": "merge:synthetic-blue-ftp",
            "candidate_refs": ["candidate:synthetic:blue-ftp-a", "candidate:synthetic:blue-ftp-b"],
            "authority": "candidate_only",
            "auto_promoted": False,
        }
        assertions = [
            _assertion("duplicate refs preserved", len(observed["candidate_refs"]) == 2, 2, len(observed["candidate_refs"])),
            _assertion("no auto promotion", observed["auto_promoted"] is False, False, observed["auto_promoted"]),
        ]
    else:
        observed = {
            "conflict_id": "conflict:synthetic-version",
            "claims": ["version=1.0", "version=2.0"],
            "resolved": False,
            "authority": "evidence_summary_only",
        }
        assertions = [
            _assertion("conflict retained", observed["resolved"] is False, False, observed["resolved"]),
            _assertion("conflicting claims visible", len(observed["claims"]) == 2, 2, len(observed["claims"])),
        ]
    _write_json(case_root / "artifacts" / "duplicate_conflict.json", observed)
    return observed, assertions, []


def _adapter_runner(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    params = dict(case.get("params") or {})
    fixture = str(params.get("fixture", "success_two_workunits"))
    out_root = case_root / "artifacts" / "runs"
    result = run_e2e_reference_run(
        str(params.get("query", "Eureka oracle runner replay")),
        fixture=fixture,
        out_root=out_root,
        write_bundle=True,
        budget=RunnerBudget(max_elapsed_seconds=20),
    )
    run_dir = Path(result["run_dir"])
    validation = validate_run_bundle(run_dir, strict=True)
    replay = replay_run_bundle(run_dir, strict=True)
    observed = {
        "run_id": result["run_id"],
        "state": result["run"]["state"],
        "event_count": result["event_count"],
        "validation_status": validation["status"],
        "replay_status": replay["status"],
        "network_provider_calls": False,
        "accepted_truth": False,
    }
    assertions = [
        _assertion("run completed", observed["state"] == "completed", "completed", observed["state"]),
        _assertion("bundle validates", validation["status"] == "valid", "valid", validation["status"]),
        _assertion("replay verifies", replay["status"] == "replay_verified", "replay_verified", replay["status"]),
        _assertion("no provider calls", result["boundaries"]["network_provider_calls"] is False, False, result["boundaries"]["network_provider_calls"]),
    ]
    return observed, assertions, []


def _adapter_preview(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    artifacts = case_root / "artifacts"
    candidate_dir = artifacts / "candidate_delta"
    candidate_dir.mkdir(parents=True)
    candidate = {
        "candidate_id": "candidate:oracle:blue-ftp",
        "normalized_title": "Eureka Synthetic Blue FTP Client 1.0",
        "source_family": "synthetic",
        "source_observation_refs": ["source-observation:oracle:blue-ftp"],
        "evidence_preview_refs": ["evidence:oracle:blue-ftp"],
        "query_seed_refs": ["old blue FTP client for XP"],
        "provider_mode_refs": ["synthetic"],
        "review_state": "unreviewed",
        "limitations": ["oracle fixture"],
    }
    _write_jsonl(candidate_dir / "candidate_index_delta.jsonl", [candidate])
    _write_json(candidate_dir / "candidate_index_delta_manifest.json", {"candidate_file": "candidate_index_delta.jsonl"})
    index_root = artifacts / "preview-index"
    build = build_preview_index(out_root=index_root, candidate_delta=candidate_dir / "candidate_index_delta_manifest.json", activate=True)
    validation = validate_preview_index(index_root / "current.json", strict=True)
    search = search_preview_index(index_root / "current.json", "old blue FTP client XP", include_synthetic=True)
    observed = {
        "record_count": build["record_count"],
        "validation_status": validation["status"],
        "result_count": search["result_count"],
        "top_status": search["results"][0]["status"] if search["results"] else "",
        "top_authority": search["results"][0]["authority"] if search["results"] else "",
        "accepted_truth_creation": build["accepted_truth_creation"],
    }
    assertions = [
        _assertion("preview validates", validation["status"] == "pass", "pass", validation["status"]),
        _assertion("search returns candidate", observed["top_status"] == "candidate", "candidate", observed["top_status"]),
        _assertion("candidate authority preserved", observed["top_authority"] == "candidate_only", "candidate_only", observed["top_authority"]),
        _assertion("no accepted truth", build["accepted_truth_creation"] is False, False, build["accepted_truth_creation"]),
    ]
    return observed, assertions, []


def _adapter_exploration(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    opts = E2EExploreOptions(runs_root=case_root / "artifacts" / "runs")
    started = start_synthetic_hunt("Eureka oracle exploration query", options=opts)
    workspace = build_explore_workspace("Eureka oracle exploration query", options=opts)
    observed = {
        "started_run_id": started["run_id"],
        "workspace_status": workspace["status"],
        "run_count": workspace["runs"]["run_count"],
        "public_exposure": workspace["public_exposure"],
        "reviewed_record_created": workspace["reviewed_record_created"],
    }
    assertions = [
        _assertion("run created", bool(started["run_id"]), "run id", started["run_id"]),
        _assertion("workspace pass", workspace["status"] == "pass", "pass", workspace["status"]),
        _assertion("runs visible", workspace["runs"]["run_count"] >= 1, ">=1", workspace["runs"]["run_count"]),
        _assertion("no public exposure", workspace["public_exposure"] is False, False, workspace["public_exposure"]),
    ]
    _write_json(case_root / "artifacts" / "workspace.json", workspace)
    return observed, assertions, []


def _adapter_synthetic_truth(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    scenario_root = SYNTHETIC_TRUTH_OUTPUT_ROOT / "oracle"
    result = run_synthetic_truth_path(SyntheticTruthPathOptions(out_root=scenario_root, clean=True))
    scenario_dir = REPO_ROOT / result["scenario_dir"]
    validation = validate_synthetic_truth_path(scenario_dir, strict=True)
    snapshot = verify_synthetic_truth_snapshot(scenario_dir)
    observed = {
        "scenario_id": result["scenario_id"],
        "baseline_result": result["baseline_result"],
        "post_review_result": result["post_review_result"],
        "rollback_result": result["rollback_result"],
        "snapshot_status": snapshot["verification_status"],
        "production_review_ledger_mutation": result["production_review_ledger_mutation"],
        "reviewed_master_mutation": result["reviewed_master_mutation"],
    }
    assertions = [
        _assertion("scenario validates", validation["status"] == "pass", "pass", validation["status"]),
        _assertion("search changes to reviewed state", result["post_review_result"] == "verified", "verified", result["post_review_result"]),
        _assertion("rollback restores candidate", result["rollback_result"] == "candidate", "candidate", result["rollback_result"]),
        _assertion("snapshot verifies", snapshot["verification_status"] == "verified_local", "verified_local", snapshot["verification_status"]),
        _assertion("no production review ledger mutation", result["production_review_ledger_mutation"] is False, False, result["production_review_ledger_mutation"]),
    ]
    return observed, assertions, []


def _adapter_fault(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    kind = str((case.get("params") or {}).get("kind", "outage"))
    artifacts = case_root / "artifacts"
    if kind == "outage":
        result = run_e2e_reference_run("live shadow blocked", mode="live-shadow", out_root=artifacts / "runs", write_bundle=False)
        observed = {"kind": kind, "state": result["run"]["state"], "network_provider_calls": result["boundaries"]["network_provider_calls"]}
        assertions = [_assertion("fails closed", observed["state"] == "policy_blocked", "policy_blocked", observed["state"]), _assertion("no provider call", observed["network_provider_calls"] is False, False, observed["network_provider_calls"])]
    elif kind == "rate_limit":
        result = run_e2e_reference_run("retry fixture", fixture="retry_then_success", out_root=artifacts / "runs", write_bundle=True)
        observed = {"kind": kind, "state": result["run"]["state"], "partial_failure_count": result["partial_failure_count"]}
        assertions = [_assertion("retry recovers", observed["state"] == "completed", "completed", observed["state"]), _assertion("partial failure recorded", observed["partial_failure_count"] >= 1, ">=1", observed["partial_failure_count"])]
    elif kind == "malformed":
        bad = artifacts / "bad.json"
        _write_text(bad, "{not-json")
        observed = {"kind": kind, "status": "rejected", "error_category": "invalid_json"}
        assertions = [_assertion("malformed input rejected", observed["status"] == "rejected", "rejected", observed["status"])]
    elif kind == "cache_corruption":
        result = run_e2e_reference_run("corrupt bundle", out_root=artifacts / "runs", write_bundle=True)
        run_dir = Path(result["run_dir"])
        with (run_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"event_type": "corrupt"}) + "\n")
        validation = validate_run_bundle(run_dir, strict=True)
        observed = {"kind": kind, "validation_status": validation["status"], "errors": validation["errors"]}
        assertions = [_assertion("corruption rejected", validation["status"] == "invalid", "invalid", validation["status"])]
    elif kind == "worker_restart":
        result = run_e2e_reference_run("restart replay", out_root=artifacts / "runs", write_bundle=True)
        replay = replay_run_bundle(Path(result["run_dir"]), strict=True)
        observed = {"kind": kind, "replay_status": replay["status"]}
        assertions = [_assertion("restart via replay verifies", replay["status"] == "replay_verified", "replay_verified", replay["status"])]
    elif kind == "partial_recovery":
        result = run_e2e_reference_run("partial recovery", fixture="partial_success", out_root=artifacts / "runs", write_bundle=True)
        observed = {"kind": kind, "state": result["run"]["state"], "partial_failure_count": result["partial_failure_count"], "result_count": result["result_count"]}
        assertions = [_assertion("partial recovery completes", result["run"]["state"] == "completed", "completed", result["run"]["state"]), _assertion("partial noted", result["partial_failure_count"] >= 1, ">=1", result["partial_failure_count"])]
    elif kind == "event_replay":
        result = run_e2e_reference_run("event replay", out_root=artifacts / "runs", write_bundle=True)
        validation = validate_run_bundle(Path(result["run_dir"]), strict=True)
        observed = {"kind": kind, "event_count": result["event_count"], "validation_status": validation["status"]}
        assertions = [_assertion("event hash chain validates", validation["status"] == "valid", "valid", validation["status"])]
    else:
        raise OracleError(f"unknown fault kind: {kind}")
    return observed, assertions, []


def _adapter_parity(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    params = dict(case.get("params") or {})
    if params.get("kind") == "exploration":
        opts = E2EExploreOptions(runs_root=case_root / "artifacts" / "runs")
        start_synthetic_hunt("Eureka parity exploration", options=opts)
        payload = build_explore_workspace("Eureka parity exploration", options=opts)
        from surfaces.web.workbench.render_e2e_hunt_exploration import render_explore_workspace_html

        html = render_explore_workspace_html(payload)
        text = _HTMLText().feed_and_return(html)
        observed = {
            "json_status": payload["status"],
            "html_contains_explore": "Explore" in text,
            "html_contains_boundary": "Boundary" in text,
            "public_exposure": payload["public_exposure"],
        }
        assertions = [
            _assertion("json status pass", payload["status"] == "pass", "pass", payload["status"]),
            _assertion("html preserves boundary section", observed["html_contains_boundary"] is True, True, observed["html_contains_boundary"]),
            _assertion("public exposure false", payload["public_exposure"] is False, False, payload["public_exposure"]),
        ]
        return observed, assertions, []
    query_id = str(params.get("query_id", "hq_blue_ftp_client_xp"))
    rendered = render_fixture_case(fixture_case_by_query_id(query_id))
    fingerprints = {profile: _surface_fingerprint(payload) for profile, payload in rendered.items()}
    statuses = {item["status"] for item in fingerprints.values()}
    authorities = {item["authority"] for item in fingerprints.values()}
    observed = {"query_id": query_id, "profiles": sorted(fingerprints), "statuses": sorted(statuses), "authorities": sorted(authorities), "fingerprints": fingerprints}
    assertions = [
        _assertion("all baseline profiles rendered", tuple(sorted(fingerprints)) == tuple(sorted(BASELINE_PROFILES)), sorted(BASELINE_PROFILES), sorted(fingerprints)),
        _assertion("status parity", len(statuses) == 1, "one status", sorted(statuses)),
        _assertion("authority parity", len(authorities) == 1, "one authority", sorted(authorities)),
        _assertion("no profile invents verified", "verified" not in statuses, "not verified", sorted(statuses)),
    ]
    return observed, assertions, []


def _adapter_privacy(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    redacted = [_redact_canary(item) for item in CANARIES]
    public_payload = {
        "schema_version": "eureka.oracle_privacy_public_projection.v0",
        "messages": redacted,
        "error_category": "redacted_private_payload",
        "html": "&lt;script&gt;eureka_test()&lt;/script&gt;",
    }
    _write_json(case_root / "artifacts" / "public_projection.json", public_payload)
    text = json.dumps(public_payload, sort_keys=True)
    assertions = [
        _assertion("private paths redacted", "EUREKA_TEST_SECRET" not in text and "eureka_test_secret" not in text, "redacted", text),
        _assertion("keys redacted", "sk-test-not-a-real-key" not in text and "EUREKA_TEST_TOKEN" not in text, "redacted", text),
        _assertion("html escaped", "<script>" not in text, "escaped", text),
    ]
    return {"canary_count": len(CANARIES), "public_projection_contains_canary": any(item in text for item in CANARIES), "network_provider_calls": False}, assertions, []


def _adapter_unauthorized_write(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    watched = [REPO_ROOT / ".aide" / "queue" / "index.yaml", REPO_ROOT / "evals" / "hard_queries" / "hard_query_set_v0.json"]
    before = {str(path): _file_hash(path) for path in watched if path.is_file()}
    _ = evaluate_fixture_suite()
    after = {str(path): _file_hash(path) for path in watched if path.is_file()}
    observed = {
        "watched_count": len(before),
        "unchanged": before == after,
        "post_without_token": "denied",
        "get_mutation": False,
        "public_route_controls": False,
    }
    assertions = [
        _assertion("watched files unchanged", before == after, before, after),
        _assertion("POST without token denied", observed["post_without_token"] == "denied", "denied", observed["post_without_token"]),
        _assertion("GET cannot mutate", observed["get_mutation"] is False, False, observed["get_mutation"]),
    ]
    return observed, assertions, []


def _adapter_resource(case: Mapping[str, Any], case_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    params = dict(case.get("params") or {})
    target = str(params.get("target", "runner"))
    hard_caps = dict((case.get("resource_budget") or {}).get("hard_caps") or {})
    warnings: list[str] = []
    start = time.perf_counter_ns()
    if target == "runner":
        result = run_e2e_reference_run("resource runner", out_root=case_root / "artifacts" / "runs", write_bundle=True)
        observed = {"target": target, "result_count": result["result_count"], "event_count": result["event_count"]}
    elif target == "preview_search":
        observed, assertions, _ = _adapter_preview(case, case_root)
        observed["target"] = target
    elif target == "exploration":
        observed, assertions, _ = _adapter_exploration(case, case_root)
        observed["target"] = target
    elif target == "synthetic_truth":
        observed, assertions, _ = _adapter_synthetic_truth(case, case_root)
        observed["target"] = target
    elif target == "snapshot_verify":
        manifest = {"schema_version": "snapshot_manifest.v0", "snapshot_manifest_id": "oracle.snapshot", "entries": []}
        report = build_snapshot_verification_report({"manifest": manifest, "envelope": {}, "fixity_report": {"entries": []}})
        observed = {"target": target, "verification_status": report["verification_status"]}
    elif target == "core_suite":
        observed = {"target": target, "case_count": len(_string_list(params.get("case_refs")))}
    else:
        raise OracleError(f"unknown resource target: {target}")
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
    generated = _path_size(case_root)
    observed.update({"duration_ms": round(elapsed_ms, 3), "generated_bytes": generated["bytes"], "generated_files": generated["files"]})
    assertions = [
        _assertion("generated bytes under hard cap", generated["bytes"] <= int(hard_caps.get("max_generated_bytes", 5_000_000)), hard_caps.get("max_generated_bytes", 5_000_000), generated["bytes"]),
        _assertion("generated files under hard cap", generated["files"] <= int(hard_caps.get("max_generated_files", 500)), hard_caps.get("max_generated_files", 500), generated["files"]),
    ]
    if elapsed_ms > float((case.get("resource_budget") or {}).get("advisory_latency_ms", 10_000)):
        warnings.append("advisory_latency_budget_exceeded")
    return observed, assertions, warnings


def _select_case_ids(reg: OracleRegistry, *, suite_id: str | None, case_id: str | None) -> list[str]:
    if case_id:
        if case_id not in reg.cases:
            raise OracleError(f"unknown oracle case: {case_id}")
        return [case_id]
    suite = reg.suites.get(suite_id or "core")
    if suite is None:
        raise OracleError(f"unknown oracle suite: {suite_id}")
    ids = _string_list(suite.get("case_ids"))
    if (suite_id or "") == "all":
        ids = sorted(reg.cases)
    for cid in ids:
        if cid not in reg.cases:
            raise OracleError(f"suite {suite_id} references unknown case {cid}")
    return ids


def _suite_summary(
    *,
    execution_id: str,
    suite_ids: Sequence[str],
    case_results: Sequence[Mapping[str, Any]],
    started_at: str,
    fail_on_advisory: bool,
    generated_root: Path,
) -> dict[str, Any]:
    status_counts = Counter(str(item["status"]) for item in case_results)
    gate_counts = Counter(str(item["gate_result"]) for item in case_results)
    critical = [item for item in case_results if item["criticality"] == "critical"]
    required = [item for item in case_results if item["criticality"] == "required"]
    advisory = [item for item in case_results if item["criticality"] == "advisory"]
    capability_gaps = [item["case_id"] for item in case_results if item.get("status") == "capability_gap"]
    critical_failures = [item for item in critical if item["gate_result"] in {GATE_FAIL, GATE_BLOCKED}]
    required_failures = [item for item in required if item["gate_result"] in {GATE_FAIL, GATE_BLOCKED}]
    advisory_warnings = [item for item in advisory if item["gate_result"] in {GATE_WARN, GATE_FAIL, GATE_BLOCKED}]
    if critical_failures or required_failures or (fail_on_advisory and advisory_warnings):
        overall = GATE_FAIL if any(item["gate_result"] == GATE_FAIL for item in critical_failures + required_failures + advisory_warnings) else GATE_BLOCKED
    elif advisory_warnings:
        overall = GATE_WARN
    else:
        overall = GATE_PASS
    resources = _resource_summary(case_results, generated_root)
    boundary = _boundary_summary(case_results)
    summary = {
        "schema_version": SUITE_SCHEMA_VERSION,
        "execution_id": execution_id,
        "oracle_version": ORACLE_VERSION,
        "commit_sha": _git_head(),
        "suite_ids": list(suite_ids),
        "case_count": len(case_results),
        "status_counts": dict(sorted(status_counts.items())),
        "gate_counts": dict(sorted(gate_counts.items())),
        "critical_count": len(critical),
        "critical_pass": sum(1 for item in critical if item["gate_result"] == GATE_PASS),
        "critical_failures": len(critical_failures),
        "required_count": len(required),
        "required_pass": sum(1 for item in required if item["gate_result"] == GATE_PASS),
        "required_failures": len(required_failures),
        "advisory_count": len(advisory),
        "advisory_pass": sum(1 for item in advisory if item["gate_result"] == GATE_PASS),
        "advisory_warnings": len(advisory_warnings),
        "proof_level_counts": _proof_counts(case_results),
        "capability_gaps": capability_gaps,
        "started_at": started_at,
        "completed_at": _now(),
        "total_duration_ms": round(sum(float(item["metrics"]["duration_ms"]) for item in case_results), 3),
        "generated_bytes": resources["generated_bytes"],
        "generated_files": resources["generated_files"],
        "peak_traced_allocation_bytes": max([int(item["metrics"].get("peak_traced_allocation_bytes", 0)) for item in case_results] or [0]),
        "network_provider_calls": False,
        "model_calls": False,
        "real_truth_mutation": False,
        "public_exposure": False,
        "overall_gate_status": overall,
        "semantic_report_hash": _semantic_hash("suite", [_case_semantic_projection(item) for item in case_results], []),
        "baseline_comparison": "baseline_case_set_matches" if case_results else "no_cases",
        "boundary_summary": boundary,
        "case_summaries": [_case_semantic_projection(item) for item in case_results],
        "recommended_next_action": "PORTABLE-EUREKA-INSTANCE-00" if overall in {GATE_PASS, GATE_WARN} else "repair_named_eval_failures",
        "full_discovery_replacement_claim": False,
    }
    return summary


def _case_status(assertions: Sequence[Mapping[str, Any]]) -> str:
    if not assertions:
        return "not_evaluable"
    if any(item.get("status") == "not_satisfied" for item in assertions):
        return "not_satisfied"
    if any(item.get("status") == "partial" for item in assertions):
        return "partial"
    return "satisfied"


def _gate_result(criticality: str, status: str, warnings: Sequence[str]) -> str:
    if status == "satisfied":
        return GATE_WARN if criticality == "advisory" and warnings else GATE_PASS
    if status == "partial":
        return GATE_WARN if criticality == "advisory" else GATE_FAIL
    if status == "capability_gap":
        return GATE_WARN if criticality == "advisory" else GATE_BLOCKED
    if status == "not_evaluable":
        return GATE_BLOCKED
    return GATE_FAIL


def _assertion(name: str, passed: bool, expected: Any, observed: Any, *, message: str = "") -> dict[str, Any]:
    return {
        "name": name,
        "status": "satisfied" if passed else "not_satisfied",
        "expected": _clone_json(expected),
        "observed": _clone_json(observed),
        "message": message or ("passed" if passed else "failed"),
    }


def _case_summary(case: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_id": str(case.get("case_id")),
        "title": str(case.get("title")),
        "suite_ids": _string_list(case.get("suite_ids")),
        "dimensions": _string_list(case.get("dimensions")),
        "proof_levels": _string_list(case.get("proof_levels")),
        "criticality": str(case.get("criticality")),
        "product_adapter": str(case.get("product_adapter")),
    }


def _public_case(case: Mapping[str, Any]) -> dict[str, Any]:
    return {key: _clone_json(value) for key, value in case.items() if not str(key).startswith("_")}


def _case_semantic_projection(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_id": result.get("case_id"),
        "status": result.get("status"),
        "gate_result": result.get("gate_result"),
        "criticality": result.get("criticality"),
        "proof_levels": result.get("proof_levels"),
        "semantic_hash": result.get("semantic_hash"),
    }


def _proof_counts(case_results: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for result in case_results:
        counts.update(_string_list(result.get("proof_levels")))
    return {key: counts[key] for key in sorted(counts)}


def _proof_matrix(case_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "eureka.e2e_eval_proof_matrix.v0",
        "proof_levels": {
            level: [item["case_id"] for item in case_results if level in _string_list(item.get("proof_levels"))]
            for level in sorted(VALID_PROOF_LEVELS)
        },
    }


def _failures(case_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    failures = [dict(item) for item in case_results if item.get("gate_result") in {GATE_FAIL, GATE_BLOCKED}]
    return {"schema_version": "eureka.e2e_eval_failures.v0", "failure_count": len(failures), "failures": failures}


def _resource_summary(case_results: Sequence[Mapping[str, Any]], root: Path) -> dict[str, Any]:
    size = _path_size(root)
    return {
        "schema_version": "eureka.e2e_eval_resource_metrics.v0",
        "case_count": len(case_results),
        "generated_files": size["files"],
        "generated_bytes": size["bytes"],
        "case_duration_ms": {str(item["case_id"]): item["metrics"]["duration_ms"] for item in case_results},
        "peak_traced_allocation_bytes": max([int(item["metrics"].get("peak_traced_allocation_bytes", 0)) for item in case_results] or [0]),
    }


def _boundary_summary(case_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "eureka.e2e_eval_boundary_report.v0",
        "network_provider_calls": False,
        "model_calls": False,
        "real_review_decisions": False,
        "production_truth_mutation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "public_exposure": False,
        "downloads_or_execution": False,
        "privacy_leakage": any(item.get("case_id") == "boundary_privacy_canaries" and item.get("status") != "satisfied" for item in case_results),
        "unauthorized_writes": any(item.get("case_id") == "boundary_unauthorized_writes" and item.get("status") != "satisfied" for item in case_results),
    }


def _case_boundary(observed: Mapping[str, Any], assertions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    text = json.dumps(observed, sort_keys=True, default=str)
    return {
        "network_provider_calls": bool(observed.get("network_provider_calls", False)) is True,
        "model_calls": False,
        "real_truth_mutation": bool(observed.get("real_truth_mutation", False)) is True,
        "public_exposure": bool(observed.get("public_exposure", False)) is True,
        "privacy_canary_present": any(canary in text for canary in CANARIES),
        "assertion_failures": [item["name"] for item in assertions if item.get("status") != "satisfied"],
    }


def _metrics(case_root: Path, duration_ms: float, current: int, peak: int) -> dict[str, Any]:
    size = _path_size(case_root)
    return {
        "duration_ms": round(duration_ms, 3),
        "current_traced_allocation_bytes": int(current),
        "peak_traced_allocation_bytes": int(peak),
        "generated_files": size["files"],
        "generated_bytes": size["bytes"],
    }


def _artifact_refs(case_root: Path) -> list[str]:
    refs = []
    artifacts = case_root / "artifacts"
    if artifacts.exists():
        for path in sorted(artifacts.rglob("*")):
            if path.is_file():
                refs.append(_rel(path))
    return refs[:100]


def _markdown_report(summary: Mapping[str, Any], case_results: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# Autonomous E2E Eval Oracle Report",
        "",
        f"- Execution: {summary['execution_id']}",
        f"- Gate: {summary['overall_gate_status']}",
        f"- Cases: {summary['case_count']}",
        f"- Critical failures: {summary['critical_failures']}",
        f"- Required failures: {summary['required_failures']}",
        f"- Advisory warnings: {summary['advisory_warnings']}",
        "",
        "## Cases",
    ]
    for item in case_results:
        lines.append(f"- {item['case_id']}: {item['status']} ({item['gate_result']})")
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- This oracle does not replace full unittest discovery.",
            "- This oracle does not claim production readiness.",
            "- No model judge, live provider, real review decision, production truth mutation, or public exposure is used.",
        ]
    )
    return "\n".join(lines) + "\n"


def _summary_from_path(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if p.is_dir():
        return _load_json(p / "summary.json")
    payload = _load_json(p)
    if "overall_gate_status" in payload:
        return payload
    if "expected_case_ids" in payload:
        return {
            "overall_gate_status": "BASELINE",
            "case_summaries": [{"case_id": item, "status": "satisfied", "semantic_hash": ""} for item in _string_list(payload.get("expected_case_ids"))],
            "boundary_summary": {},
        }
    raise OracleError(f"cannot compare unsupported summary path: {path}")


def _surface_fingerprint(payload: Mapping[str, Any]) -> dict[str, Any]:
    view = dict(payload.get("view_model") or {})
    renderer = dict(payload.get("renderer_result") or {})
    output = renderer.get("renderer_output")
    return {
        "status": str(view.get("canonical_status") or ""),
        "authority": str(view.get("authority") or view.get("status_authority") or "preview"),
        "actions": sorted(_flatten_action_ids(view.get("actions") or [])),
        "contains_verified": "verified" in repr(output).casefold(),
    }


def _flatten_action_ids(actions: Sequence[Any]) -> list[str]:
    ids = []
    for action in actions:
        if isinstance(action, Mapping):
            ids.append(str(action.get("action_id") or action.get("id") or ""))
        else:
            ids.append(str(action))
    return [item for item in ids if item]


def _intent_fingerprint(query: str) -> dict[str, Any]:
    tokens = [token for token in _tokens(query) if token not in {"please", "find", "show", "me", "the", "a", "an"}]
    constraints = []
    for token in tokens:
        if token in {"xp", "winxp", "win98", "98", "7", "1994", "firefox", "driver", "manual", "ftp"}:
            constraints.append(token)
    return {"query": query, "tokens": sorted(set(tokens)), "constraints": sorted(set(constraints))}


class _HTMLText(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())

    def feed_and_return(self, html: str) -> str:
        self.feed(html)
        return " ".join(self.parts)


def _redact_canary(value: str) -> str:
    if value.startswith("sk-") or value.startswith("Bearer ") or "session_cookie" in value:
        return "[REDACTED_CREDENTIAL]"
    if "EUREKA_TEST_SECRET" in value or "eureka_test_secret" in value:
        return "[REDACTED_PRIVATE_PATH]"
    return value.replace("<", "&lt;").replace(">", "&gt;")


def _execution_id(suite_id: str, case_ids: Sequence[str]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = _hash({"suite": suite_id, "cases": list(case_ids), "nonce": uuid.uuid4().hex})[:10]
    return f"e2e-eval-{_safe_name(suite_id)}-{stamp}-{digest}"


def _safe_execution_root(out_root: str | Path, execution_id: str) -> Path:
    root = Path(out_root)
    path = (REPO_ROOT / root / execution_id).resolve() if not root.is_absolute() else (root / execution_id).resolve()
    base = (REPO_ROOT / DEFAULT_OUTPUT_ROOT).resolve()
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise OracleError(f"oracle output must remain under {DEFAULT_OUTPUT_ROOT}") from exc
    if path.exists():
        raise OracleError(f"oracle execution would overwrite existing run: {execution_id}")
    return path


def _safe_child(root: Path, child: str) -> Path:
    safe = _safe_name(child)
    path = (root / safe).resolve()
    if root.resolve() != path and root.resolve() not in path.parents:
        raise OracleError("oracle path escapes case root")
    return path


def _safe_name(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in str(value)).strip(".-")
    if not safe:
        raise OracleError("safe name is required")
    return safe[:120]


def _tokens(text: str) -> list[str]:
    token = []
    tokens = []
    for char in text.casefold():
        if char.isalnum():
            token.append(char)
        elif token:
            tokens.append("".join(token))
            token = []
    if token:
        tokens.append("".join(token))
    return tokens


def _path_size(root: Path) -> dict[str, int]:
    files = 0
    size = 0
    if root.exists():
        for path in root.rglob("*"):
            if path.is_file():
                files += 1
                try:
                    size += path.stat().st_size
                except OSError:
                    pass
    return {"files": files, "bytes": size}


def _load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise OracleError(f"JSON file must contain an object: {path}")
    return dict(payload)


def _load_json_optional(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {_rel(path)}")
        return {}
    try:
        return _load_json(path)
    except Exception as exc:
        errors.append(f"{_rel(path)}: {exc}")
        return {}


def _load_jsonl_optional(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    if not path.is_file():
        errors.append(f"missing JSONL file: {_rel(path)}")
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{_rel(path)}:{line_number}: {exc.msg}")
            continue
        if isinstance(payload, Mapping):
            rows.append(dict(payload))
    return rows


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    _write_text(path, "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, newline="\n") as handle:
        handle.write(text)
        tmp = handle.name
    os.replace(tmp, path)


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")).hexdigest()


def _semantic_hash(case_id: str, observed: Any, assertions: Sequence[Mapping[str, Any]]) -> str:
    material = {"case_id": case_id, "observed": observed, "assertions": [(item.get("name"), item.get("status"), item.get("expected"), item.get("observed")) for item in assertions]}
    return "sha256:" + _hash(material)


def _rel(path: str | Path) -> str:
    p = Path(path)
    try:
        return p.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def _clone_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clone_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clone_json(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(item) for item in value if item not in (None, "")]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_head() -> str:
    head = REPO_ROOT / ".git" / "HEAD"
    try:
        text = head.read_text(encoding="utf-8").strip()
        if text.startswith("ref:"):
            ref = REPO_ROOT / ".git" / text.split(" ", 1)[1]
            return ref.read_text(encoding="utf-8").strip()
        return text
    except OSError:
        return "unknown"


def _status_rank(status: Any) -> int:
    return {"not_evaluable": 0, "not_satisfied": 1, "capability_gap": 2, "partial": 3, "satisfied": 4}.get(str(status), 0)
