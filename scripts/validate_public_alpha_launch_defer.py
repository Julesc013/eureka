from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

RESULT_PATH = "control/inventory/public_alpha_launch_defer_result.json"
REASON_PATH = "control/inventory/public_alpha_launch_defer_reason_matrix.json"

REQUIRED_DOCS = [
    "docs/operations/PUBLIC_ALPHA_LAUNCH_DEFERRED.md",
    "docs/operations/ACTIVE_DISCOVERY_NEXT_PLAN.md",
    "control/audits/public-alpha-launch-defer-00-v0/README.md",
    "control/audits/public-alpha-launch-defer-00-v0/archive_org_metadata_search_gate.md",
    "control/audits/public-alpha-launch-defer-00-v0/next_queue.md",
    "control/audits/public-alpha-launch-defer-00-v0/validation.md",
]

NEXT_QUEUE = [
    "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00",
    "QUERY-TO-SOURCE-ACTION-PLANNER-00",
    "CANDIDATE-INDEX-RUNTIME-00",
    "SOURCE-ACTION-LIVE-METADATA-PILOTS-00",
    "SCOUT-RUNTIME-00",
    "REVIEW-BATCH-00",
    "SEED-BATCH-FRONTIER-MEDIA-00",
    "SEED-BATCH-LEGACY-SOFTWARE-00",
    "SNAPSHOT-REFRESH-00",
    "PUBLIC-ALPHA-REASSESS-00",
]
POST_DEFER_QUEUE_PREFIXES = (
    "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-",
    "QUERY-TO-SOURCE-ACTION-PLANNER-",
    "CANDIDATE-INDEX-RUNTIME-",
    "SCOUT-RUNTIME-",
    "REVIEW-BATCH-",
    "SEED-BATCH-",
    "SNAPSHOT-REFRESH-",
    "PUBLIC-ALPHA-REASSESS-",
    "PUBLIC-SEARCH-UX-",
    "LIVE-METADATA-PILOT-BATCH-",
    "REVIEW-LIVE-METADATA-CANDIDATES-",
    "LOCAL-APPLY-LIVE-METADATA-PREVIEWS-",
    "TSIS-",
    "INDEXLESS-LIVE-SEARCH-FALLBACK-",
    "REVIEW-LEDGER-",
    "WORKBENCH-RUN-REVIEW-PROJECTION-",
    "SURFACE-KERNEL-",
    "BASELINE-RENDERERS-",
    "HARD-QUERY-EVAL-",
    "REVIEWED-SEED-CORPUS-",
    "MANUAL-OBSERVATION-BATCH-",
    "HUMAN-REVIEW-BATCH-",
    "HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-",
    "SOURCE-FOUNDRY-",
    "IA-METADATA-PROVIDER-WIRING-",
    "IA-SOURCE-OBSERVATION-CACHE-DELTA-",
    "IA-CANDIDATE-INDEX-REFRESH-",
    "IA-EVIDENCE-LEDGER-SUMMARY-",
    "REVIEW-IA-CANDIDATES-",
    "REVIEWED-CORPUS-SEED-BATCH-",
    "SOURCE-SNAPSHOT-",
    "ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-",
    "QUEUE-HANDOFF-DRIFT-REPAIR-",
    "GENERATED-ARTIFACT-DRIFT-REPAIR-",
    "CONTRACT-SCHEMA-DRIFT-REPAIR-",
    "EXTERNAL-FULL-DISCOVERY-",
    "WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE",
    "WAITING_FOR_EXTERNAL_FULL_DISCOVERY",
    "WAITING_FOR_USER_HARDWARE_DETAILS",
)

FALSE_FIELDS = [
    "deployment_performed",
    "public_launch_performed",
    "staging_deployment_performed",
    "public_alpha_launch_approval_active",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "downloads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
]


def validate_public_alpha_launch_defer(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    result = _load_json(root / RESULT_PATH, RESULT_PATH, errors)
    reason = _load_json(root / REASON_PATH, REASON_PATH, errors)

    _validate_result(result, errors)
    _validate_reason_matrix(reason, errors)
    _validate_preserved_evidence(root, errors)
    _validate_docs(root, errors)
    _validate_queue(root, errors)
    _validate_no_approval_file(root, errors)

    return {
        "schema_version": "public_alpha_launch_defer_validation.v0",
        "task": "PUBLIC-ALPHA-LAUNCH-DEFER-00",
        "status": "invalid" if errors else "pass",
        "deferred_task": result.get("deferred_task"),
        "recommended_next_task": result.get("recommended_next_task"),
        "archive_org_wide_metadata_search_required": bool(
            result.get("required_next_capability", {}).get("must_support_archive_org_wide_metadata_search")
        ),
        "deployment_performed": bool(result.get("deployment_performed")),
        "public_launch_performed": bool(result.get("public_launch_performed")),
        "errors": errors,
    }


def _validate_result(result: Mapping[str, Any], errors: list[str]) -> None:
    if result.get("schema_version") != "public_alpha_launch_defer_result.v0":
        errors.append("defer result schema_version mismatch")
    if result.get("task") != "PUBLIC-ALPHA-LAUNCH-DEFER-00":
        errors.append("defer result task mismatch")
    if result.get("deferred_task") != "PUBLIC-ALPHA-LAUNCH-00":
        errors.append("defer result must defer PUBLIC-ALPHA-LAUNCH-00")
    if result.get("status") != "deferred":
        errors.append("defer result status must be deferred")
    if result.get("reason_code") != "insufficient_candidate_discovery_and_index_coverage":
        errors.append("defer result reason_code mismatch")
    if result.get("recommended_next_task") != "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00":
        errors.append("defer result recommended_next_task mismatch")

    for field in FALSE_FIELDS:
        if result.get(field) is not False:
            errors.append(f"defer result must set {field}=false")

    preserved = result.get("preserved_evidence")
    if not isinstance(preserved, Mapping):
        errors.append("defer result preserved_evidence must be an object")
    else:
        if preserved.get("public_alpha_launch_candidate_result") != "pass":
            errors.append("launch candidate evidence must be preserved as pass")
        if preserved.get("public_alpha_deploy_dry_run_result") != "pass":
            errors.append("deploy dry-run evidence must be preserved as pass")

    capability = result.get("required_next_capability")
    if not isinstance(capability, Mapping):
        errors.append("defer result required_next_capability must be an object")
    else:
        if capability.get("must_support_archive_org_wide_metadata_search") is not True:
            errors.append("Archive.org-wide metadata search requirement must be true")
        endpoints = capability.get("allowed_initial_endpoints")
        if not isinstance(endpoints, list):
            errors.append("allowed_initial_endpoints must be a list")
        else:
            for endpoint in (
                "https://archive.org/advancedsearch.php",
                "https://archive.org/services/search/v1/scrape",
                "https://archive.org/metadata/{identifier}",
            ):
                if endpoint not in endpoints:
                    errors.append(f"missing allowed initial endpoint: {endpoint}")

    if result.get("next_queue") != NEXT_QUEUE:
        errors.append("defer result next_queue does not match required queue")


def _validate_reason_matrix(reason: Mapping[str, Any], errors: list[str]) -> None:
    if reason.get("schema_version") != "public_alpha_launch_defer_reason_matrix.v0":
        errors.append("reason matrix schema_version mismatch")
    if reason.get("status") != "deferred":
        errors.append("reason matrix status must be deferred")
    reasons = reason.get("reasons")
    if not isinstance(reasons, list) or len(reasons) < 4:
        errors.append("reason matrix must include at least four reasons")
    else:
        ids = {item.get("reason_id") for item in reasons if isinstance(item, Mapping)}
        for reason_id in (
            "reviewed_corpus_too_small",
            "active_discovery_not_public_ready",
            "archive_org_wide_metadata_search_required",
            "no_broad_crawling_or_downloads",
        ):
            if reason_id not in ids:
                errors.append(f"reason matrix missing {reason_id}")

    refs = reason.get("source_references")
    if not isinstance(refs, list):
        errors.append("reason matrix source_references must be a list")
    else:
        urls = {item.get("url") for item in refs if isinstance(item, Mapping)}
        for url in (
            "https://archive.org/developers/item-search-apis.html",
            "https://archive.org/developers/md-read.html",
            "https://archive.org/developers/metadata-schema/index.html",
        ):
            if url not in urls:
                errors.append(f"reason matrix missing source reference: {url}")


def _validate_preserved_evidence(root: Path, errors: list[str]) -> None:
    launch_candidate = _load_json(root / "control/inventory/public_alpha_launch_candidate_result.json", "launch candidate result", errors)
    dry_run = _load_json(root / "control/inventory/public_alpha_deploy_dry_run_result.json", "deploy dry-run result", errors)
    launch = _load_json(root / "control/inventory/public_alpha_launch_result.json", "public alpha launch result", errors)

    if launch_candidate.get("status") != "pass":
        errors.append("public alpha launch candidate validator evidence must remain pass")
    if dry_run.get("status") != "pass":
        errors.append("public alpha deploy dry-run evidence must remain pass")
    if launch.get("deployment_performed") is not False:
        errors.append("existing launch result must keep deployment_performed=false")
    if launch.get("public_launch_performed") is not False:
        errors.append("existing launch result must keep public_launch_performed=false")
    if launch.get("production_readiness_claimed") is not False:
        errors.append("existing launch result must keep production_readiness_claimed=false")
    if launch.get("public_launch_readiness_claimed") is not False:
        errors.append("existing launch result must keep public_launch_readiness_claimed=false")


def _validate_docs(root: Path, errors: list[str]) -> None:
    required_phrases = {
        "docs/operations/PUBLIC_ALPHA_LAUNCH_DEFERRED.md": [
            "Status: `DEFERRED`",
            "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00",
            "Archive.org-wide metadata",
            "No deployment",
        ],
        "docs/operations/ACTIVE_DISCOVERY_NEXT_PLAN.md": [
            "Archive.org-Wide Metadata Search Requirement",
            "candidate records",
            "review queue",
            "No downloads",
        ],
    }
    for rel in REQUIRED_DOCS:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required doc: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in required_phrases.get(rel, []):
            if phrase.lower() not in text.lower():
                errors.append(f"{rel} missing phrase: {phrase}")


def _validate_queue(root: Path, errors: list[str]) -> None:
    queue = root / ".aide/queue/index.yaml"
    if not queue.exists():
        errors.append("missing .aide/queue/index.yaml")
        return
    text = queue.read_text(encoding="utf-8")
    current = _current_task_id(text)
    if current != "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00" and not current.startswith(POST_DEFER_QUEUE_PREFIXES):
        errors.append("queue current recommended task must be active discovery or a later blocked repair/readiness task")
    if current == "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00":
        for item in NEXT_QUEUE:
            if f"  - {item}" not in text:
                errors.append(f"queue missing planned task: {item}")


def _current_task_id(queue_text: str) -> str:
    for line in queue_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("current_recommended_task:"):
            return stripped.split(":", 1)[1].strip().split()[0]
    return ""


def _validate_no_approval_file(root: Path, errors: list[str]) -> None:
    if (root / "control/approvals/public-alpha-launch-00-approval.json").exists():
        errors.append("public alpha launch approval file must not be active while launch is deferred")


def _load_json(path: Path, label: str, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"missing required file: {label}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {label}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PUBLIC-ALPHA-LAUNCH-DEFER-00.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_alpha_launch_defer()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"public alpha launch defer validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
