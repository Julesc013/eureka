#!/usr/bin/env python3
"""Validate LOCAL-08 local review and reviewed-index rebuild."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from runtime.evidence_ledger import EvidenceCandidateRecord, EvidenceReviewStatus
from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_review import get_review_item, rebuild_reviewed_index, record_review_decision
from runtime.local_service import LocalServiceApp, create_local_http_server
from runtime.review_queue import ReviewItemRecord, ReviewQueueStatus
from runtime.source_cache import SourceCacheEntry, SourceCacheStatus


TASK_ID = "LOCAL-08"
NEXT_TASK = "LOCAL-09"
TOKEN = "local-review-token"
POLICIES = {
    "control/policies/local_operator_auth_policy.json": "local_operator_auth_policy.v0",
    "control/policies/local_review_decision_policy.json": "local_review_decision_policy.v0",
    "control/policies/local_review_rebuild_policy.json": "local_review_rebuild_policy.v0",
    "control/policies/local_review_ui_policy.json": "local_review_ui_policy.v0",
    "control/policies/local_review_side_effect_policy.json": "local_review_side_effect_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_review_rebuild_inventory.json": "local_review_rebuild_inventory.v0",
    "control/inventory/local_review_route_matrix.json": "local_review_route_matrix.v0",
    "control/inventory/local_review_decision_matrix.json": "local_review_decision_matrix.v0",
    "control/inventory/local_review_rebuild_result.json": "local_review_rebuild_result.v0",
    "control/inventory/local_review_smoke_result.json": "local_review_smoke_result.v0",
    "control/inventory/local_review_gap_register.json": "local_review_gap_register.v0",
    "control/inventory/local_08_leakage_baseline.json": "local_08_leakage_baseline.v0",
    "control/inventory/local_08_next_task_decision.json": "local_08_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/local_operator/__init__.py",
    "runtime/local_operator/auth.py",
    "runtime/local_operator/tokens.py",
    "runtime/local_operator/validation.py",
    "runtime/local_operator/errors.py",
    "runtime/local_review/__init__.py",
    "runtime/local_review/service.py",
    "runtime/local_review/decisions.py",
    "runtime/local_review/rebuild.py",
    "runtime/local_review/audit.py",
    "runtime/local_review/validation.py",
    "runtime/local_review/errors.py",
)
SCRIPTS = (
    "scripts/eureka_set_operator_token.py",
    "scripts/eureka_review_queue.py",
    "scripts/eureka_rebuild_reviewed_index.py",
    "scripts/eureka_local_review_smoke.py",
    "scripts/validate_local_review_rebuild.py",
)
TESTS = (
    "tests/runtime/test_local_operator_auth.py",
    "tests/runtime/test_local_review_service.py",
    "tests/runtime/test_local_review_decisions.py",
    "tests/runtime/test_local_rebuild_service.py",
    "tests/runtime/test_local_review_workbench_pages.py",
    "tests/operations/test_local_review_scripts.py",
    "tests/operations/test_local_review_rebuild_smoke.py",
)
DOCS = (
    "docs/architecture/LOCAL_REVIEW_REBUILD_LOOP.md",
    "docs/reference/LOCAL_REVIEW_API.md",
    "docs/reference/LOCAL_OPERATOR_AUTH.md",
    "docs/operations/LOCAL_REVIEW_REBUILD_RUNBOOK.md",
    "docs/operations/LOCAL_REVIEW_NON_CLAIMS.md",
)
AUDIT_ROOT = Path("control/audits/local-08-review-rebuild-ui-v0")
AUDIT_FILES = (
    "README.md",
    "local_08_report.json",
    "review_rebuild_summary.md",
    "operator_auth_summary.md",
    "route_matrix.md",
    "decision_matrix.md",
    "rebuild_boundary.md",
    "smoke_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_review_queue.html",
    "generated/sample_review_item.html",
    "generated/sample_rebuild_page.html",
    "generated/sample_review_decision.json",
    "generated/sample_rebuild_result.json",
    "generated/sample_smoke_result.json",
    "generated/sample_summary.md",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
)
FORBIDDEN_VOCABULARY = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE", "task", "agent", "prompt")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-08 review/rebuild validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in {**POLICIES, **INVENTORIES}.items()}
    report = load_json(root / AUDIT_ROOT / "local_08_report.json", "local_08_report.v0", errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors, warnings)
    validate_files(root, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    service = validate_review_runtime(root, errors)
    validate_scripts(root, errors)
    validate_queue_state(root, errors)
    validate_report(report, errors)
    validate_leakage(root, payloads.get("control/inventory/local_08_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_review_rebuild_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "operator_auth_added": all((root / rel).is_file() for rel in RUNTIME_FILES[:5]),
        "review_service_added": all((root / rel).is_file() for rel in RUNTIME_FILES[5:]),
        "review_ui_added": service.get("review_ui_added", False),
        "rebuild_ui_added": service.get("rebuild_ui_added", False),
        "review_decision_persisted": service.get("review_decision_persisted", False),
        "accepted_review_included_in_rebuild": service.get("accepted_review_included_in_rebuild", False),
        "rejected_blocked_reviews_excluded": service.get("rejected_blocked_reviews_excluded", False),
        "rebuild_requires_token": service.get("rebuild_requires_token", False),
        "review_decision_requires_token": service.get("review_decision_requires_token", False),
        "source_probe_executed": False,
        "workunit_execution_performed": False,
        "agent_execution_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    auth = payloads.get("control/policies/local_operator_auth_policy.json", {})
    for key in (
        "operator_token_required_for_mutations",
        "default_token_forbidden",
        "token_may_be_provided_by_cli",
        "token_may_be_stored_as_hash_in_instance_config",
        "raw_token_storage_forbidden",
        "token_logging_forbidden",
        "localhost_only_mutations",
    ):
        if auth.get(key) is not True:
            errors.append(f"auth policy {key} must be true")
    for key in ("lan_operator_access_enabled", "deployment_enabled"):
        if auth.get(key) is not False:
            errors.append(f"auth policy {key} must be false")

    decisions = payloads.get("control/policies/local_review_decision_policy.json", {})
    if decisions.get("allowed_decisions") != ["accept", "reject", "block", "request_more_evidence", "note_only"]:
        errors.append("decision policy allowed_decisions mismatch")
    for key in (
        "accept_requires_local_only_confirmation",
        "reject_requires_reason",
        "block_requires_reason",
        "request_more_evidence_requires_reason",
        "decisions_are_local_review_state_only",
        "decisions_do_not_mutate_index_directly",
        "decisions_do_not_accept_global_truth",
        "decisions_do_not_clear_rights",
        "decisions_do_not_certify_malware_safety",
    ):
        if decisions.get(key) is not True:
            errors.append(f"decision policy {key} must be true")

    rebuild = payloads.get("control/policies/local_review_rebuild_policy.json", {})
    if rebuild.get("includes_review_statuses") != ["accepted"]:
        errors.append("rebuild policy include statuses mismatch")
    for key in ("rebuild_requires_operator_token", "public_index_store_mutated"):
        if rebuild.get(key) is not True:
            errors.append(f"rebuild policy {key} must be true")
    for key in (
        "input_stores_mutated",
        "master_index_mutated",
        "site_dist_writes_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if rebuild.get(key) is not False:
            errors.append(f"rebuild policy {key} must be false")

    ui = payloads.get("control/policies/local_review_ui_policy.json", {})
    for key in ("review_ui_enabled", "rebuild_ui_enabled", "localhost_only", "operator_token_required_for_mutations", "get_routes_read_only", "post_routes_mutating_operator_only", "no_download_install_execute_controls", "no_source_probe_controls", "no_workunit_execution_controls"):
        if ui.get(key) is not True:
            errors.append(f"ui policy {key} must be true")
    if ui.get("lan_enabled") is not False:
        errors.append("ui policy lan_enabled must be false")

    side = payloads.get("control/policies/local_review_side_effect_policy.json", {})
    for key in ("review_decision_mutation_allowed", "index_rebuild_allowed"):
        if side.get(key) is not True:
            errors.append(f"side-effect policy {key} must be true")
    for key in (
        "source_probe_allowed",
        "workunit_execution_allowed",
        "agent_execution_allowed",
        "download_allowed",
        "install_execution_allowed",
        "model_provider_allowed",
        "source_sync_allowed",
        "site_dist_writes_allowed",
        "master_index_mutation_allowed",
        "lan_operations_allowed",
    ):
        if side.get(key) is not False:
            errors.append(f"side-effect policy {key} must be false")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str], warnings: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_review_rebuild_inventory.json", {})
    if inventory.get("runtime_packages") != ["runtime/local_operator", "runtime/local_review"]:
        errors.append("review inventory runtime packages mismatch")
    for key in ("review_ui_enabled", "rebuild_ui_enabled", "operator_token_required"):
        if inventory.get(key) is not True:
            errors.append(f"review inventory {key} must be true")
    for key in (
        "lan_enabled",
        "source_probe_execution_enabled",
        "workunit_execution_enabled",
        "agent_execution_enabled",
        "master_index_mutation_enabled",
        "site_dist_writes_enabled",
        "deployment_performed",
    ):
        if inventory.get(key) is not False:
            errors.append(f"review inventory {key} must be false")

    result = payloads.get("control/inventory/local_review_rebuild_result.json", {})
    for key in (
        "operator_auth_added",
        "review_service_added",
        "review_ui_added",
        "rebuild_ui_added",
        "review_decision_persisted",
        "accepted_review_included_in_rebuild",
        "rejected_blocked_reviews_excluded",
        "rebuild_requires_token",
        "review_decision_requires_token",
    ):
        if result.get(key) is not True:
            errors.append(f"review result {key} must be true")
    for key in (
        "source_probe_executed",
        "workunit_execution_performed",
        "agent_execution_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if result.get(key) is not False:
            errors.append(f"review result {key} must be false")

    decision = payloads.get("control/inventory/local_08_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "LOCAL-09 \u2014 Deterministic local worker runner":
        errors.append("LOCAL-08 next task decision must point to LOCAL-09")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != "LOCAL-14":
        errors.append("F0 must remain deferred")
    if decision.get("lan_can_start") is not False or decision.get("worker_execution_enabled") is not False:
        errors.append("LOCAL-08 next task flags mismatch")

    leakage = payloads.get("control/inventory/local_08_leakage_baseline.json", {})
    if leakage.get("local_08_increased_leakage") is not False:
        errors.append("LOCAL-08 leakage baseline must not increase leakage")
    if leakage.get("runtime_leakage_gate_status_after") == "fail":
        warnings.append("pre-existing runtime leakage gate still fails")


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*RUNTIME_FILES, *SCRIPTS, *TESTS, *DOCS):
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty file: {rel}")
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"empty audit file: {(AUDIT_ROOT / rel).as_posix()}")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        path = root / rel
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module or ""]
            for module in modules:
                if any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_review_runtime(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {
        "review_ui_added": False,
        "rebuild_ui_added": False,
        "review_decision_persisted": False,
        "accepted_review_included_in_rebuild": False,
        "rejected_blocked_reviews_excluded": False,
        "rebuild_requires_token": False,
        "review_decision_requires_token": False,
    }
    with tempfile.TemporaryDirectory(prefix="eureka-local08-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"temp instance init failed: {init.stdout}{init.stderr}")
            return result
        write_operator_token_record(instance, TOKEN)
        runtime = open_local_appliance(instance)
        try:
            seed = seed_review_records(runtime)
            app = LocalServiceApp(runtime)
            review_page = app.handle("GET", "/review")
            rebuild_page = app.handle("GET", "/rebuild")
            result["review_ui_added"] = review_page.status_code == 200 and "Review queue" in review_page.body
            result["rebuild_ui_added"] = rebuild_page.status_code == 200 and "Reviewed-index rebuild" in rebuild_page.body
            missing = app.handle("POST", f"/review/{seed['accepted_review_item_id']}/decision", body="decision=accept")
            invalid = app.handle(
                "POST",
                "/rebuild",
                body="operator_token=wrong-token&operator_label=validator",
            )
            result["review_decision_requires_token"] = missing.status_code == 401
            result["rebuild_requires_token"] = invalid.status_code == 401
            decision = record_review_decision(
                runtime,
                seed["accepted_review_item_id"],
                "accept",
                None,
                "validator",
                True,
            )
            record_review_decision(runtime, seed["rejected_review_item_id"], "reject", "not enough support", "validator", False)
            record_review_decision(runtime, seed["blocked_review_item_id"], "block", "blocked locally", "validator", False)
            detail = get_review_item(runtime, seed["accepted_review_item_id"])
            result["review_decision_persisted"] = bool(decision.get("review_decision_persisted") and detail.get("decisions"))
            dry_run = rebuild_reviewed_index(runtime, "validator", dry_run=True)
            apply = rebuild_reviewed_index(runtime, "validator", dry_run=False)
            search = runtime.public_index.search("local08 accepted artifact", limit=10)
            records = apply.get("records", [])
            result["accepted_review_included_in_rebuild"] = bool(records and search)
            excluded = apply.get("excluded", [])
            excluded_ids = {str(item.get("review_item_id")) for item in excluded if isinstance(item, Mapping)}
            result["rejected_blocked_reviews_excluded"] = seed["rejected_review_item_id"] in excluded_ids and seed["blocked_review_item_id"] in excluded_ids
            if dry_run.get("dry_run") is not True or apply.get("dry_run") is not False:
                errors.append("dry-run/apply rebuild flags mismatch")
            for key, value in result.items():
                if not value:
                    errors.append(f"runtime validation failed: {key}")
            integrity = runtime.check_integrity()
            if integrity.get("status") != "pass":
                errors.append("runtime integrity failed after review rebuild")
        finally:
            close_local_appliance(runtime)

        handle = None
        thread = None
        try:
            handle, thread = start_loopback_server(instance, TOKEN)
            smoke = run(
                root,
                "python",
                "scripts/eureka_local_review_smoke.py",
                "--base-url",
                f"http://127.0.0.1:{handle.server_port}",
                "--operator-token",
                TOKEN,
                "--json",
            )
            if smoke.returncode != 0:
                errors.append(f"review smoke failed: {smoke.stdout}{smoke.stderr}")
        finally:
            if handle is not None:
                handle.shutdown()
                if thread is not None:
                    thread.join(timeout=5)
    return result


def seed_review_records(runtime: Any) -> dict[str, str]:
    cache = SourceCacheEntry(
        entry_id="sce_local08_accept",
        source_id="source.local08",
        source_family="local_fixture",
        trust_lane="local_review",
        request_id="req_local08_accept",
        response_id="resp_local08_accept",
        observation_id="obs_local08_accept",
        normalized_observation_id="norm_local08_accept",
        response_fingerprint="sha256:local08accept",
        status=SourceCacheStatus.CACHED,
        payload={
            "normalized_observation": {
                "normalized_fields": {
                    "title": "Local08 Accepted Artifact",
                    "description": "Accepted local review projection sample",
                    "version": "1.0",
                }
            }
        },
        limitations=("local validation sample",),
    )
    evidence = EvidenceCandidateRecord(
        evidence_id="evi_local08_accept",
        source_id=cache.source_id,
        source_cache_entry_id=cache.entry_id,
        observation_id=cache.observation_id,
        normalized_observation_id=cache.normalized_observation_id,
        claim_kind="metadata_claim",
        claim_subject="local08 accepted artifact",
        claim_payload={
            "normalized_fields": {
                "title": "Local08 Accepted Artifact",
                "description": "Accepted local review projection sample",
            }
        },
        status=EvidenceReviewStatus.NEEDS_REVIEW,
        limitations=("local validation sample",),
    )
    accepted = ReviewItemRecord(
        review_item_id="rvi_local08_accept",
        subject_kind="evidence_candidate",
        subject_id=evidence.evidence_id,
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        evidence_id=evidence.evidence_id,
        source_cache_entry_id=cache.entry_id,
        summary="Review local08 accepted artifact",
    )
    rejected = ReviewItemRecord(
        review_item_id="rvi_local08_reject",
        subject_kind="evidence_candidate",
        subject_id="evi_local08_reject",
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        summary="Review local08 rejected artifact",
    )
    blocked = ReviewItemRecord(
        review_item_id="rvi_local08_block",
        subject_kind="evidence_candidate",
        subject_id="evi_local08_block",
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        summary="Review local08 blocked artifact",
    )
    runtime.source_cache.write_cache_entry(cache)
    runtime.evidence_ledger.write_evidence_candidate(evidence)
    runtime.review_queue.enqueue_review_item(accepted)
    runtime.review_queue.enqueue_review_item(rejected)
    runtime.review_queue.enqueue_review_item(blocked)
    return {
        "accepted_review_item_id": accepted.review_item_id,
        "rejected_review_item_id": rejected.review_item_id,
        "blocked_review_item_id": blocked.review_item_id,
    }


def validate_scripts(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-local08-cli-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        if run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json").returncode != 0:
            errors.append("CLI temp instance init failed")
            return
        set_token = run(root, "python", "scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", TOKEN, "--json")
        if set_token.returncode != 0:
            errors.append(f"set token CLI failed: {set_token.stdout}{set_token.stderr}")
            return
        runtime = open_local_appliance(instance)
        try:
            seed = seed_review_records(runtime)
        finally:
            close_local_appliance(runtime)
        list_cmd = run(root, "python", "scripts/eureka_review_queue.py", "--instance", str(instance), "--json", "list")
        show_cmd = run(root, "python", "scripts/eureka_review_queue.py", "--instance", str(instance), "--json", "show", "--id", seed["accepted_review_item_id"])
        decide_cmd = run(
            root,
            "python",
            "scripts/eureka_review_queue.py",
            "--instance",
            str(instance),
            "--json",
            "decide",
            "--id",
            seed["accepted_review_item_id"],
            "--decision",
            "accept",
            "--operator-token",
            TOKEN,
            "--local-only-confirmed",
        )
        rebuild_cmd = run(
            root,
            "python",
            "scripts/eureka_rebuild_reviewed_index.py",
            "--instance",
            str(instance),
            "--operator-token",
            TOKEN,
            "--apply",
            "--json",
        )
        for label, completed in (("review list", list_cmd), ("review show", show_cmd), ("review decide", decide_cmd), ("rebuild apply", rebuild_cmd)):
            if completed.returncode != 0:
                errors.append(f"{label} CLI failed: {completed.stdout}{completed.stderr}")


def validate_queue_state(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/LOCAL-08/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/LOCAL-09/task.yaml", errors)
    if "current_recommended_task: LOCAL-09" not in queue:
        errors.append("queue index must point to LOCAL-09")
    if "id: LOCAL-08" not in queue or "status: completed" not in queue:
        errors.append("queue index must mark LOCAL-08 completed")
    if "id: LOCAL-09" not in queue or "status: queued" not in queue:
        errors.append("queue index must include queued LOCAL-09")
    if "deferred_until: LOCAL-14" not in queue:
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "recommended_next: LOCAL-09" not in task:
        errors.append("LOCAL-08 task must recommend LOCAL-09")
    if "Deterministic local worker runner" not in next_task:
        errors.append("LOCAL-09 task title mismatch")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-09 \u2014 Deterministic local worker runner":
        errors.append("LOCAL-08 audit report must recommend LOCAL-09")
    for key in (
        "operator_auth_added",
        "review_service_added",
        "review_ui_added",
        "rebuild_ui_added",
        "review_decision_persisted",
        "accepted_review_included_in_rebuild",
        "rejected_blocked_reviews_excluded",
        "rebuild_requires_token",
        "review_decision_requires_token",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
    ):
        if report.get(key) is not True:
            errors.append(f"LOCAL-08 report {key} must be true")
    for key in (
        "worker_execution_enabled",
        "lan_enabled",
        "source_probe_executed",
        "workunit_execution_performed",
        "agent_execution_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "local_08_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"LOCAL-08 report {key} must be false")


def validate_leakage(root: Path, leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if before >= 0 and after > before:
        errors.append("LOCAL-08 increased runtime leakage")
    scan = run_leakage_scan(root)
    scan_count = int(scan.get("summary", {}).get("new_violation_count", -1))
    if before >= 0 and scan_count > before:
        errors.append("current leakage scan exceeds recorded LOCAL-08 baseline")
    if scan.get("gate_report", {}).get("status") == "fail":
        warnings.append("runtime leakage gate fails with pre-existing findings")


def run_leakage_scan(root: Path) -> Mapping[str, Any]:
    import audit_runtime_architecture_leakage as leakage

    policy = leakage.load_json(root / leakage.DEFAULT_POLICY)
    allowlist = leakage.load_json(root / leakage.DEFAULT_ALLOWLIST)
    return leakage.build_leakage_audit(root, policy, allowlist, policy_errors=[])


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {relpath(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {relpath(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {relpath(path)}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"schema_version mismatch for {relpath(path)}")
    return payload


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing text file: {relpath(path)}")
        return ""


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=root, text=True, capture_output=True, check=False)


def start_loopback_server(instance: Path, token: str) -> tuple[Any, threading.Thread]:
    ready = threading.Event()
    holder: dict[str, Any] = {}

    def serve() -> None:
        handle = create_local_http_server(instance, host="127.0.0.1", port=0, operator_token=token)
        holder["handle"] = handle
        ready.set()
        try:
            handle.httpd.serve_forever()
        finally:
            handle.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    if not ready.wait(timeout=10):
        raise RuntimeError("local review validation server did not start")
    return holder["handle"], thread


def relpath(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
