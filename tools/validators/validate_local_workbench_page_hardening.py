#!/usr/bin/env python3
"""Validate LOCAL-06 workbench page hardening evidence."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.local_queue_progress import (
    f0_deferred_or_past_local_closeout,
    queue_current_or_advanced,
    queue_task_available,
    queue_task_completed,
)
from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.service import LocalServiceApp
from runtime.index.public import PublicIndexRecord, PublicIndexStore
from surfaces.web.workbench.local_html import (
    build_absence_page_view,
    build_home_page_view,
    build_object_page_view,
    build_search_page_view,
    build_source_page_view,
    build_status_page_view,
    render_absence_page,
    render_home_page,
    render_object_page,
    render_search_page,
    render_source_page,
    render_status_page,
    validate_local_workbench_page,
)


TASK_ID = "LOCAL-06"
NEXT_TASK = "LOCAL-07"
POLICIES = {
    "control/policies/local_html_page_hardening_policy.json": "local_html_page_hardening_policy.v0",
    "control/policies/local_workbench_non_claim_policy.json": "local_workbench_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_workbench_page_hardening_inventory.json": "local_workbench_page_hardening_inventory.v0",
    "control/inventory/local_workbench_page_hardening_result.json": "local_workbench_page_hardening_result.v0",
    "control/inventory/local_workbench_non_claim_matrix.json": "local_workbench_non_claim_matrix.v0",
    "control/inventory/local_html_gap_register.json": "local_html_gap_register.v0",
    "control/inventory/local_06_leakage_baseline.json": "local_06_leakage_baseline.v0",
    "control/inventory/local_06_next_task_decision.json": "local_06_next_task_decision.v0",
}
RUNTIME_FILES = (
    "surfaces/web/workbench/local_html/__init__.py",
    "surfaces/web/workbench/local_html/html.py",
    "surfaces/web/workbench/local_html/pages.py",
    "surfaces/web/workbench/local_html/templates.py",
    "surfaces/web/workbench/local_html/view_models.py",
    "surfaces/web/workbench/local_html/validation.py",
    "surfaces/web/workbench/local_html/errors.py",
)
AUDIT_ROOT = Path("control/audits/local-06-page-hardening-v0")
AUDIT_FILES = (
    "README.md",
    "local_06_report.json",
    "page_hardening_summary.md",
    "status_page_summary.md",
    "search_page_summary.md",
    "object_page_summary.md",
    "source_page_summary.md",
    "absence_page_summary.md",
    "non_claim_matrix.md",
    "smoke_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_home.html",
    "generated/sample_search.html",
    "generated/sample_object.html",
    "generated/sample_source.html",
    "generated/sample_absence.html",
    "generated/sample_status.html",
    "generated/sample_page_hardening_result.json",
    "generated/sample_smoke_result.json",
    "generated/sample_summary.md",
)
DOCS = (
    "docs/reference/LOCAL_WORKBENCH_VIEW_MODELS.md",
    "docs/operations/LOCAL_WORKBENCH_PAGE_HARDENING.md",
    "docs/operations/LOCAL_WORKBENCH_NON_CLAIMS.md",
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
FORBIDDEN_VOCABULARY = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE")
FORBIDDEN_CLAIM_TEXT = (
    "production ready",
    "public launch ready",
    "globally complete",
    "exhaustive coverage",
    "legal approval",
    "rights cleared",
    "malware safe",
    "installability certified",
    "source truth accepted",
    "evidence truth accepted",
    "master index mutated",
    "deployment performed",
)


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
        print("LOCAL-06 workbench page hardening validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_06_report.json", "local_06_report.v0", errors)
    validate_policy_payloads(payloads, errors)
    validate_inventory_payloads(payloads, errors, warnings)
    validate_files(root, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    service = validate_pages_and_service(root, errors)
    validate_queue(root, errors)
    validate_report(report, errors)
    validate_leakage(root, payloads.get("control/inventory/local_06_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_workbench_page_hardening_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "home_page_hardened": service.get("home_page_hardened", False),
        "search_page_hardened": service.get("search_page_hardened", False),
        "object_page_hardened": service.get("object_page_hardened", False),
        "source_page_hardened": service.get("source_page_hardened", False),
        "absence_page_hardened": service.get("absence_page_hardened", False),
        "status_page_hardened": service.get("status_page_hardened", False),
        "json_api_still_passed": service.get("json_api_still_passed", False),
        "workbench_smoke_passed": service.get("workbench_smoke_passed", False),
        "mutation_controls_found": False,
        "external_assets_found": False,
        "forbidden_claims_found": False,
    }


def validate_policy_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    hardening = payloads.get("control/policies/local_html_page_hardening_policy.json", {})
    for key in (
        "status_page_store_health_required",
        "search_result_provenance_required",
        "object_provenance_required",
        "source_page_local_scope_required",
        "absence_limitations_required",
        "non_claim_banner_required",
        "no_mutation_controls",
        "no_external_assets",
        "no_javascript_required",
        "no_lan_controls",
        "no_deployment_controls",
    ):
        if hardening.get(key) is not True:
            errors.append(f"hardening policy {key} must be true")
    non_claim = payloads.get("control/policies/local_workbench_non_claim_policy.json", {})
    if len(non_claim.get("forbidden_claims", [])) != 12:
        errors.append("non-claim policy must list 12 forbidden claims")
    for wording in ("local_only", "current_index_only", "reviewed_local_projection", "candidate_or_reviewed_state", "limitations_visible", "warnings_visible"):
        if wording not in non_claim.get("required_wording_classes", []):
            errors.append(f"non-claim policy missing wording class {wording}")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str], warnings: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_workbench_page_hardening_inventory.json", {})
    if inventory.get("pages_hardened") != ["home", "search", "object", "source", "absence", "status"]:
        errors.append("page hardening inventory pages_hardened mismatch")
    for key in ("non_claim_banner_enabled", "store_status_visible", "provenance_visible", "absence_layers_visible", "unavailable_capabilities_visible"):
        if inventory.get(key) is not True:
            errors.append(f"page hardening inventory {key} must be true")
    for key in ("mutation_controls_enabled", "external_assets_enabled", "lan_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"page hardening inventory {key} must be false")
    result = payloads.get("control/inventory/local_workbench_page_hardening_result.json", {})
    for key in (
        "home_page_hardened",
        "search_page_hardened",
        "object_page_hardened",
        "source_page_hardened",
        "absence_page_hardened",
        "status_page_hardened",
        "non_claim_banner_present",
        "store_status_visible",
        "provenance_fields_visible",
        "absence_checked_layers_visible",
        "absence_unchecked_layers_visible",
        "json_api_still_passed",
        "workbench_smoke_passed",
    ):
        if result.get(key) is not True:
            errors.append(f"page hardening result {key} must be true")
    for key in ("mutation_controls_found", "external_assets_found", "forbidden_claims_found", "lan_enabled", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if result.get(key) is not False:
            errors.append(f"page hardening result {key} must be false")
    matrix = payloads.get("control/inventory/local_workbench_non_claim_matrix.json", {})
    for row in matrix.get("claims", []):
        if row.get("found") is not False:
            errors.append(f"forbidden claim was marked found: {row.get('claim')}")
    decision = payloads.get("control/inventory/local_06_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "LOCAL-07 \u2014 Operator-gated WorkUnit queue":
        errors.append("LOCAL-06 next task decision must point to LOCAL-07")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != "LOCAL-14":
        errors.append("F0 must remain deferred until LOCAL-14")
    leakage = payloads.get("control/inventory/local_06_leakage_baseline.json", {})
    if leakage.get("local_06_increased_leakage") is not False:
        errors.append("LOCAL-06 leakage baseline must not increase leakage")
    if leakage.get("runtime_leakage_gate_status_after") == "fail":
        warnings.append("pre-existing runtime leakage gate still fails")


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*RUNTIME_FILES, "scripts/validate_local_workbench_page_hardening.py", *DOCS):
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
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
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
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_pages_and_service(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {
        "home_page_hardened": False,
        "search_page_hardened": False,
        "object_page_hardened": False,
        "source_page_hardened": False,
        "absence_page_hardened": False,
        "status_page_hardened": False,
        "json_api_still_passed": False,
        "workbench_smoke_passed": False,
    }
    validate_rendered_samples(errors, result)
    with tempfile.TemporaryDirectory(prefix="eureka-local-hardening-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("temp instance init failed")
            return result
        with PublicIndexStore.open(instance / "db" / "public_index.sqlite") as store:
            store.write_record(sample_record())
        before = tree_digest(instance)
        runtime = None
        try:
            runtime = open_local_appliance(instance, read_only=True)
            app = LocalServiceApp(runtime)
            for path, marker in (
                ("/status", "Store status"),
                ("/search?q=sampleproject", "Provenance references"),
                ("/object/pir_local06_sample", "Normalized fields"),
                ("/source/source.local.sample", "Source coverage shown here is local"),
                ("/absence?q=not-present", "Unchecked and deferred layers"),
                ("/", "Unavailable capabilities"),
            ):
                response = app.handle("GET", path)
                if response.status_code >= 500 or "text/html" not in response.content_type or marker not in response.body:
                    errors.append(f"hardened HTML route missing marker {marker}: {path}")
                validate_page_text(response.body, errors)
            json_status = app.handle("GET", "/api/v1/status")
            json_search = app.handle("GET", "/api/v1/search", "q=sampleproject")
            result["json_api_still_passed"] = json_status.status_code == 200 and json_search.status_code == 200
        finally:
            if runtime is not None:
                close_local_appliance(runtime)
        after = tree_digest(instance)
        if before != after:
            errors.append("page hardening routes mutated temp instance")
        result["workbench_smoke_passed"] = run_server_smoke(root, instance, errors)
    return result


def validate_rendered_samples(errors: list[str], result: dict[str, bool]) -> None:
    status = {
        "status": "pass",
        "runtime": {
            "instance_id": "sample",
            "instance_schema_version": 1,
            "instance_root": "sample-root",
            "store_count": 4,
            "stores": {"public_index": {"relative_path": "db/public_index.sqlite", "opened": True, "integrity_status": "pass", "schema_version": "public_index_store.v0"}},
            "migration_needed": False,
            "read_only": True,
            "server_enabled": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
        "public_index": {"record_count": 1, "rebuild_count": 0, "source_ref_count": 1, "evidence_ref_count": 1, "review_ref_count": 1, "source_counts": {"source.local.sample": 1}},
        "warnings": [],
        "limitations": [],
    }
    record = sample_record().to_dict()
    pages = {
        "home_page_hardened": render_home_page(build_home_page_view(status)),
        "search_page_hardened": render_search_page(build_search_page_view("sampleproject", {"result_count": 1, "results": [record], "warnings": [], "limitations": []})),
        "object_page_hardened": render_object_page(build_object_page_view(record["record_id"], record)),
        "source_page_hardened": render_source_page(build_source_page_view(record["source_id"], {"result_count": 1, "records": [record], "warnings": [], "limitations": []})),
        "absence_page_hardened": render_absence_page(build_absence_page_view("missing", {"absence": {"result_count": 0, "checked_sources": []}, "warnings": [], "limitations": []})),
        "status_page_hardened": render_status_page(build_status_page_view(status)),
    }
    markers = {
        "home_page_hardened": "Unavailable capabilities",
        "search_page_hardened": "Provenance references",
        "object_page_hardened": "Normalized fields",
        "source_page_hardened": "Source coverage shown here is local",
        "absence_page_hardened": "Unchecked and deferred layers",
        "status_page_hardened": "Store status",
    }
    for key, html in pages.items():
        try:
            validate_local_workbench_page(html)
            validate_page_text(html, errors)
        except Exception as exc:
            errors.append(f"{key} failed validation: {exc}")
        result[key] = markers[key] in html and "Local appliance prototype" in html


def validate_page_text(html: str, errors: list[str]) -> None:
    lowered = html.lower()
    if any(item in lowered for item in ("method=\"post\"", "formmethod=\"post\"", "<script", "javascript:", "href=\"https://", "src=\"https://")):
        errors.append("page contains mutation control or external asset")
    for claim in FORBIDDEN_CLAIM_TEXT:
        if claim in lowered:
            errors.append(f"page contains forbidden claim: {claim}")


def run_server_smoke(root: Path, instance: Path, errors: list[str]) -> bool:
    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            ["python", "scripts/eureka_local_server.py", "--instance", str(instance), "--host", "127.0.0.1", "--port", "0", "--json-startup"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        startup_line = process.stdout.readline() if process.stdout is not None else ""
        if not startup_line:
            errors.append("local server did not report startup")
            return False
        startup = json.loads(startup_line)
        smoke = run(root, "python", "scripts/eureka_local_workbench_smoke.py", "--base-url", str(startup["base_url"]), "--json")
        if smoke.returncode != 0:
            errors.append(f"workbench smoke failed: {smoke.stdout}{smoke.stderr}")
            return False
        payload = json.loads(smoke.stdout)
        return payload.get("status") == "pass" and payload.get("json_api_still_passed") is True
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/LOCAL-06/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/LOCAL-07/task.yaml", errors)
    if not queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to LOCAL-07")
    if not queue_task_completed(root, TASK_ID):
        errors.append("queue index must mark LOCAL-06 completed")
    if not queue_task_available(root, NEXT_TASK):
        errors.append("queue index must include queued LOCAL-07")
    if not f0_deferred_or_past_local_closeout(root):
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "recommended_next: LOCAL-07" not in task:
        errors.append("LOCAL-06 task must recommend LOCAL-07")
    if "Operator-gated WorkUnit queue" not in next_task:
        errors.append("LOCAL-07 task title mismatch")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-07 \u2014 Operator-gated WorkUnit queue":
        errors.append("LOCAL-06 audit report must recommend LOCAL-07")
    for key in (
        "home_page_hardened",
        "search_page_hardened",
        "object_page_hardened",
        "source_page_hardened",
        "absence_page_hardened",
        "status_page_hardened",
        "non_claim_banner_present",
        "store_status_visible",
        "provenance_fields_visible",
        "absence_checked_layers_visible",
        "absence_unchecked_layers_visible",
        "json_api_still_passed",
        "workbench_smoke_passed",
        "server_implemented",
        "html_workbench_implemented",
    ):
        if report.get(key) is not True:
            errors.append(f"LOCAL-06 report {key} must be true")
    for key in (
        "mutation_controls_found",
        "external_assets_found",
        "forbidden_claims_found",
        "workunit_runtime_implemented",
        "lan_enabled",
        "source_probe_executed",
        "review_mutation_performed",
        "index_rebuild_performed",
        "deployment_performed",
        "local_06_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"LOCAL-06 report {key} must be false")


def validate_leakage(root: Path, leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if before >= 0 and after > before:
        errors.append("LOCAL-06 increased runtime leakage")
    scan = run_leakage_scan(root)
    if scan:
        scan_count = int(scan.get("summary", {}).get("new_violation_count", -1))
        if scan_count > before and before >= 0:
            errors.append("current leakage scan exceeds recorded LOCAL-06 baseline")
        if scan.get("gate_report", {}).get("status") == "fail":
            warnings.append("runtime leakage gate fails with pre-existing findings")


def sample_record() -> PublicIndexRecord:
    return PublicIndexRecord(
        record_id="pir_local06_sample",
        source_id="source.local.sample",
        source_cache_entry_id="sce_local06_sample",
        evidence_id="evc_local06_sample",
        review_item_id="rvi_local06_sample",
        review_decision_id="rvd_local06_sample",
        title="sampleproject",
        description="Synthetic reviewed record for page hardening",
        normalized_fields={"name": "sampleproject", "summary": "Synthetic local record"},
        searchable_text="sampleproject synthetic reviewed local record",
        source_family="fixture_metadata",
        trust_lane="synthetic_reviewed",
    )


def run_leakage_scan(root: Path) -> Mapping[str, Any]:
    import audit_runtime_architecture_leakage as leakage

    policy = leakage.load_json(root / leakage.DEFAULT_POLICY)
    allowlist = leakage.load_json(root / leakage.DEFAULT_ALLOWLIST)
    return leakage.build_leakage_audit(root, policy, allowlist, policy_errors=[])


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name.endswith("-journal") or path.name.endswith("-wal") or path.name.endswith("-shm"):
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.as_posix()}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {path.as_posix()}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"schema_version mismatch for {path.as_posix()}")
    return payload


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing text file: {path.as_posix()}")
        return ""


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=root, text=True, capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
