from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
INSPECTOR = REPO_ROOT / "scripts" / "inspect_staged_pack.py"
MANIFEST_VALIDATOR = REPO_ROOT / "scripts" / "validate_local_staging_manifest.py"
EXAMPLES_ROOT = REPO_ROOT / "examples" / "local_staging_manifests"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "staged-pack-inspector-v0"
AUDIT_REPORT = AUDIT_ROOT / "staged_pack_inspector_report.json"
DOCS = {
    REPO_ROOT / "docs" / "operations" / "STAGED_PACK_INSPECTION.md",
    REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_MANIFEST_FORMAT.md",
    REPO_ROOT / "docs" / "architecture" / "LOCAL_QUARANTINE_STAGING_MODEL.md",
    REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_PATH_POLICY.md",
    REPO_ROOT / "docs" / "reference" / "STAGING_REPORT_PATH_CONTRACT.md",
    REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md",
}
REQUIRED_AUDIT_FILES = {
    "README.md",
    "INSPECTOR_SUMMARY.md",
    "COMMAND_USAGE.md",
    "JSON_OUTPUT_MODEL.md",
    "HUMAN_OUTPUT_MODEL.md",
    "REDACTION_REVIEW.md",
    "NO_MUTATION_REVIEW.md",
    "EXAMPLE_INSPECTION_RESULTS.md",
    "FUTURE_STAGING_TOOL_IMPACT.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_STEPS.md",
    "staged_pack_inspector_report.json",
}
LOCAL_STATE_DIRS = {
    ".eureka-local",
    ".eureka-cache",
    ".eureka-staging",
    ".eureka-reports",
}
HARD_FALSE_FIELDS = (
    "model_calls_performed",
    "mutation_performed",
    "staging_performed",
    "import_performed",
    "indexing_performed",
    "upload_performed",
    "master_index_mutation_performed",
    "runtime_mutation_performed",
    "network_performed",
    "public_search_mutated",
    "local_index_mutated",
)
REQUIRED_DOC_PHRASES = {
    "read-only",
    "no staging runtime",
    "does not stage",
    "does not import",
    "does not index",
    "does not upload",
    "public search",
    "local index",
    "master index",
    "candidate",
}
PROHIBITED_CLAIMS = {
    "staging runtime is implemented",
    "local staging exists as runtime",
    "staged packs affect public search",
    "staged packs affect local index",
    "accepted by the master index",
    "rights clearance approved",
    "malware safety approved",
    "canonical truth established",
}
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects|Temp|tmp)[\\/]|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|"
    r"/(Users|home|var/folders|private/tmp|tmp)/)",
    re.IGNORECASE,
)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Staged Pack Inspector v0.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_staged_pack_inspector()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["ok"] else 1


def validate_staged_pack_inspector() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _require_file(INSPECTOR, errors)
    _require_file(MANIFEST_VALIDATOR, errors)
    _validate_audit_pack(errors)
    _validate_docs(errors)
    _validate_no_local_state_dirs(errors)
    inspection = _run_inspector(errors)
    _validate_inspection_output(inspection, errors)

    return {
        "schema_version": "staged_pack_inspector_validation.v0",
        "validator_id": "staged_pack_inspector_validator_v0",
        "ok": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "inspector_script": _rel(INSPECTOR),
        "audit_root": _rel(AUDIT_ROOT),
        "docs_checked": sorted(_rel(path) for path in DOCS),
        "example_count": _example_count(),
        "inspection_summary": inspection.get("summary") if isinstance(inspection, Mapping) else None,
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _validate_audit_pack(errors: list[str]) -> None:
    if not AUDIT_ROOT.exists():
        errors.append(f"{_rel(AUDIT_ROOT)}: audit pack is missing.")
        return
    existing = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"{_rel(AUDIT_ROOT)}: missing audit files {missing}.")
    report = _load_json(AUDIT_REPORT, errors)
    if isinstance(report, Mapping):
        expected_false = {
            "staging_runtime_implemented",
            "staging_performed",
            "import_performed",
            "indexing_performed",
            "upload_performed",
            "runtime_mutation_performed",
            "master_index_mutation_performed",
            "network_performed",
            "model_calls_performed",
        }
        if report.get("status") != "implemented_read_only":
            errors.append(f"{_rel(AUDIT_REPORT)}: status must be implemented_read_only.")
        for field in expected_false:
            if report.get(field) is not False:
                errors.append(f"{_rel(AUDIT_REPORT)}: {field} must be false.")
        if report.get("next_recommended_milestone") != "Manual Observation Batch 0 Execution, human-operated":
            errors.append(f"{_rel(AUDIT_REPORT)}: next_recommended_milestone must name manual observation batch 0.")


def _validate_docs(errors: list[str]) -> None:
    for path in sorted(DOCS):
        text = _read_text(path, errors).lower()
        for phrase in REQUIRED_DOC_PHRASES:
            if phrase not in text:
                errors.append(f"{_rel(path)}: missing required phrase: {phrase}.")
        for claim in PROHIBITED_CLAIMS:
            if claim in text:
                errors.append(f"{_rel(path)}: prohibited claim found: {claim}.")


def _validate_no_local_state_dirs(errors: list[str]) -> None:
    for root in sorted(LOCAL_STATE_DIRS):
        if (REPO_ROOT / root).exists():
            errors.append(f"{root}/: local staging/report runtime directory must not exist.")


def _run_inspector(errors: list[str]) -> Mapping[str, Any]:
    if not INSPECTOR.exists() or not EXAMPLES_ROOT.exists():
        return {}
    completed = subprocess.run(
        [sys.executable, str(INSPECTOR), "--all-examples", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        errors.append(f"{_rel(INSPECTOR)} --all-examples --json failed with exit {completed.returncode}.")
        if completed.stderr:
            errors.append(_safe_excerpt(completed.stderr))
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(INSPECTOR)}: JSON output did not parse: {exc}.")
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _validate_inspection_output(payload: Mapping[str, Any], errors: list[str]) -> None:
    if not payload:
        return
    if payload.get("schema_version") != "staged_pack_inspection.v0":
        errors.append("inspector JSON schema_version must be staged_pack_inspection.v0.")
    if payload.get("inspector_id") != "staged_pack_inspector_v0":
        errors.append("inspector JSON inspector_id must be staged_pack_inspector_v0.")
    if payload.get("ok") is not True:
        errors.append("inspector JSON ok must be true for committed examples.")
    for field in HARD_FALSE_FIELDS:
        if payload.get(field) is not False:
            errors.append(f"inspector JSON {field} must be false.")
    inspected = payload.get("inspected_manifests")
    if not isinstance(inspected, list) or not inspected:
        errors.append("inspector JSON inspected_manifests must be a non-empty array.")
        return
    for index, item in enumerate(inspected):
        if not isinstance(item, Mapping):
            errors.append(f"inspected_manifests[{index}] must be an object.")
            continue
        if item.get("validation_status") != "passed":
            errors.append(f"inspected_manifests[{index}].validation_status must be passed.")
        guarantees = item.get("no_mutation_guarantees")
        if not isinstance(guarantees, Mapping):
            errors.append(f"inspected_manifests[{index}].no_mutation_guarantees must be an object.")
        else:
            for key, value in guarantees.items():
                if value is not False:
                    errors.append(f"inspected_manifests[{index}].no_mutation_guarantees.{key} must be false.")
        entity_summary = item.get("staged_entity_summary")
        if not isinstance(entity_summary, Mapping) or "candidate" not in str(entity_summary).lower():
            errors.append(f"inspected_manifests[{index}].staged_entity_summary must record candidate semantics.")
    serialized = json.dumps(payload)
    if PRIVATE_PATH_RE.search(serialized):
        errors.append("inspector JSON output contains an unredacted private absolute path.")
    if SECRET_VALUE_RE.search(serialized):
        errors.append("inspector JSON output contains an unredacted secret-like value.")


def _example_count() -> int:
    if not EXAMPLES_ROOT.exists():
        return 0
    return sum(1 for root in EXAMPLES_ROOT.iterdir() if root.is_dir() and (root / "LOCAL_STAGING_MANIFEST.json").is_file())


def _require_file(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"{_rel(path)}: required file is missing.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_rel(path)}: missing JSON file.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
        return None


def _read_text(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"{_rel(path)}: missing text file.")
        return ""
    return path.read_text(encoding="utf-8")


def _safe_excerpt(text: str) -> str:
    text = PRIVATE_PATH_RE.sub("<redacted-local-path>", text)
    text = SECRET_VALUE_RE.sub("<redacted-secret>", text)
    return text[:800]


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return "<explicit-local-path>"


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Staged Pack Inspector validation",
        f"status: {report['status']}",
        f"inspector_script: {report['inspector_script']}",
        f"audit_root: {report['audit_root']}",
        f"example_count: {report['example_count']}",
        f"inspection_summary: {report.get('inspection_summary')}",
    ]
    for field in HARD_FALSE_FIELDS:
        lines.append(f"{field}: {report[field]}")
    if report["errors"]:
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
