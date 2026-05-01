from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO

from pack_validator_examples import argument_error, format_all_examples, validate_all_examples


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_ROOT = REPO_ROOT / "examples" / "master_index_review_queue" / "minimal_review_queue_v0"

SCHEMA_FILES = [
    REPO_ROOT / "contracts" / "master_index" / "review_queue_manifest.v0.json",
    REPO_ROOT / "contracts" / "master_index" / "review_queue_entry.v0.json",
    REPO_ROOT / "contracts" / "master_index" / "review_decision.v0.json",
]
INVENTORY_FILES = [
    REPO_ROOT / "control" / "inventory" / "master_index" / "review_queue_policy.json",
    REPO_ROOT / "control" / "inventory" / "master_index" / "review_state_taxonomy.json",
    REPO_ROOT / "control" / "inventory" / "master_index" / "acceptance_requirements.json",
]
REQUIRED_QUEUE_FILES = {
    "REVIEW_QUEUE_MANIFEST.json",
    "README.md",
    "CHECKSUMS.SHA256",
    "queue_entries.jsonl",
    "review_decisions.jsonl",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "queue_id",
    "title",
    "status",
    "queue_entries",
    "decision_files",
    "validation_policy",
    "privacy_policy",
    "rights_policy",
    "risk_policy",
    "conflict_policy",
    "publication_policy",
    "no_runtime_implemented",
    "no_upload_implemented",
    "no_accounts_implemented",
    "no_auto_acceptance",
    "notes",
}
REQUIRED_ENTRY_FIELDS = {
    "schema_version",
    "queue_entry_id",
    "queue_id",
    "contribution_pack_ref",
    "submitted_as_status",
    "validation_status",
    "review_status",
    "privacy_classification",
    "rights_classification",
    "risk_classification",
    "proposed_changes",
    "referenced_packs",
    "evidence_summary",
    "conflict_summary",
    "reviewer_notes",
    "limitations",
    "notes",
}
REQUIRED_DECISION_FIELDS = {
    "schema_version",
    "decision_id",
    "queue_entry_id",
    "decision",
    "decision_basis",
    "reviewer_notes",
    "public_claims_allowed",
    "limitations",
}

ALLOWED_MANIFEST_STATUSES = {"draft", "local_review_example", "hosted_future", "inactive"}
ALLOWED_PACK_STATUSES = {
    "draft",
    "local_private",
    "validated_local",
    "shareable_candidate",
    "submitted",
    "quarantined",
    "review_required",
    "accepted_public",
    "rejected",
    "superseded",
}
ALLOWED_VALIDATION_STATUSES = {
    "not_checked",
    "structurally_valid",
    "structurally_invalid",
    "checksum_failed",
    "privacy_failed",
    "rights_review_required",
    "risk_review_required",
    "conflict_detected",
    "ready_for_review",
}
ALLOWED_REVIEW_STATUSES = {
    "unreviewed",
    "automated_checks_pending",
    "human_review_required",
    "accepted_public",
    "rejected",
    "superseded",
    "needs_revision",
    "quarantined",
}
ALLOWED_PRIVACY_CLASSES = {
    "public_safe",
    "local_private",
    "review_required",
    "restricted",
    "unknown",
}
ALLOWED_RIGHTS_CLASSES = {
    "public_metadata_only",
    "source_terms_apply",
    "review_required",
    "restricted",
    "unknown",
}
ALLOWED_RISK_CLASSES = {
    "metadata_only",
    "executable_reference",
    "private_data_risk",
    "credential_risk",
    "malware_review_required",
    "unknown",
}
ALLOWED_PACK_TYPES = {"source_pack", "evidence_pack", "index_pack", "contribution_pack"}
ALLOWED_DECISIONS = {"accept_public", "reject", "quarantine", "request_revision", "supersede", "defer"}
ALLOWED_DECISION_BASIS = {
    "structural_validation",
    "evidence_review",
    "source_policy_review",
    "privacy_review",
    "rights_review",
    "risk_review",
    "conflict_review",
    "manual_reviewer",
    "future_policy",
}
REQUIRED_ACCEPTANCE_REQUIREMENTS = {
    "structure_validates",
    "checksums_pass",
    "privacy_public_safe_or_reviewed",
    "rights_review_complete_or_public_scope_restricted",
    "source_evidence_provenance_present",
    "conflicts_recorded",
    "manual_or_policy_review_decision_exists",
    "no_private_paths_or_secrets",
}
PROHIBITED_KEYS = {
    "api_key",
    "auth_token",
    "credential",
    "credentials",
    "password",
    "private_key",
    "secret",
    "source_credentials",
    "token",
}
EXECUTABLE_EXTENSIONS = {
    ".app",
    ".bat",
    ".cmd",
    ".deb",
    ".dmg",
    ".exe",
    ".iso",
    ".msi",
    ".pkg",
    ".rpm",
    ".sh",
}
DATABASE_OR_CACHE_EXTENSIONS = {".cache", ".db", ".sqlite", ".sqlite3"}
PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/][^\s\"']+"),
    re.compile(r"(^|[\s\"'])(/Users|/home|/tmp|/var|/etc)/[^\s\"']+"),
    re.compile(r"\\\\[^\\\s]+\\[^\\\s]+"),
)
FORBIDDEN_CLAIM_PHRASES = (
    "rights-cleared",
    "rights cleared",
    "malware-free",
    "malware safe to run",
    "automatically accepted",
    "accepted by the live master index",
    "accepted by a live hosted master index",
    "claims canonical truth",
    "is canonical proof",
    "production-ready",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Eureka Master Index Review Queue v0 example.")
    parser.add_argument("--queue-root", help="Review queue directory to validate.")
    parser.add_argument(
        "--all-examples",
        "--known-examples",
        dest="all_examples",
        action="store_true",
        help="Validate all registered review queue examples.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require checksum coverage for every queue file.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.all_examples and args.queue_root:
        report = argument_error(
            "validate_master_index_review_queue",
            "--queue-root cannot be combined with --all-examples.",
        )
    elif args.all_examples:
        report = validate_all_examples(
            pack_type="master_index_review_queue",
            created_by="validate_master_index_review_queue",
            root_field="queue_root",
            strict=args.strict,
            validate_one=lambda root: validate_master_index_review_queue(root, strict=args.strict),
        )
    else:
        report = validate_master_index_review_queue(
            Path(args.queue_root) if args.queue_root else DEFAULT_QUEUE_ROOT,
            strict=args.strict,
        )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        if report.get("mode") in {"all_examples", "argument_error"}:
            output.write(
                format_all_examples(
                    report,
                    title="Master Index Review Queue v0 validation",
                    root_field="queue_root",
                )
            )
        else:
            output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_master_index_review_queue(queue_root: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    root = queue_root if queue_root.is_absolute() else REPO_ROOT / queue_root
    root = root.resolve()

    for schema_file in SCHEMA_FILES:
        if not schema_file.exists():
            errors.append(f"{_rel(schema_file)}: schema file is missing.")
        else:
            _load_json(schema_file, errors)

    inventory_payloads: dict[str, Any] = {}
    for inventory_file in INVENTORY_FILES:
        if not inventory_file.exists():
            errors.append(f"{_rel(inventory_file)}: inventory file is missing.")
            continue
        inventory_payloads[inventory_file.name] = _load_json(inventory_file, errors)

    _validate_inventory(inventory_payloads, errors)

    if not root.exists():
        errors.append(f"{_rel(root)}: queue root is missing.")
        return _report(root, None, [], [], errors, warnings)
    if not root.is_dir():
        errors.append(f"{_rel(root)}: queue root must be a directory.")
        return _report(root, None, [], [], errors, warnings)

    for required in sorted(REQUIRED_QUEUE_FILES):
        if not (root / required).exists():
            errors.append(f"{_rel(root / required)}: required queue file is missing.")

    manifest = _load_json(root / "REVIEW_QUEUE_MANIFEST.json", errors)
    if isinstance(manifest, Mapping):
        _validate_manifest(root, manifest, errors)
    else:
        manifest = None

    checksum_entries = _validate_checksums(root, strict=strict, errors=errors)

    entries: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    if isinstance(manifest, Mapping):
        entries = _load_manifest_jsonl_records(root, manifest.get("queue_entries"), "queue_entries", errors)
        decisions = _load_manifest_jsonl_records(root, manifest.get("decision_files"), "decision_files", errors)

    _validate_entries(entries, manifest, errors)
    _validate_decisions(decisions, entries, errors)
    _scan_tree_for_safety(root, errors)

    report = _report(root, manifest, entries, decisions, errors, warnings)
    report["checksum_entry_count"] = len(checksum_entries)
    return report


def _validate_inventory(payloads: Mapping[str, Any], errors: list[str]) -> None:
    policy = payloads.get("review_queue_policy.json")
    if isinstance(policy, Mapping):
        for flag in [
            "no_runtime_implemented",
            "no_hosted_master_index_implemented",
            "no_upload_implemented",
            "no_accounts_implemented",
            "no_auto_acceptance",
        ]:
            if policy.get(flag) is not True:
                errors.append(f"control/inventory/master_index/review_queue_policy.json: {flag} must be true.")
        accepted = set(_as_list(policy.get("accepted_input_pack_types")))
        if not {"contribution_pack", "source_pack", "evidence_pack", "index_pack"}.issubset(accepted):
            errors.append("control/inventory/master_index/review_queue_policy.json: accepted_input_pack_types is incomplete.")

    requirements = payloads.get("acceptance_requirements.json")
    if isinstance(requirements, Mapping):
        required = set(_as_list(requirements.get("future_acceptance_requires")))
        missing = REQUIRED_ACCEPTANCE_REQUIREMENTS - required
        if missing:
            errors.append(
                "control/inventory/master_index/acceptance_requirements.json: missing future acceptance requirements "
                + ", ".join(sorted(missing))
                + "."
            )


def _validate_manifest(root: Path, manifest: Mapping[str, Any], errors: list[str]) -> None:
    missing = REQUIRED_MANIFEST_FIELDS - set(manifest)
    if missing:
        errors.append(f"REVIEW_QUEUE_MANIFEST.json: missing required fields: {', '.join(sorted(missing))}.")
    if manifest.get("schema_version") != "master_index_review_queue_manifest.v0":
        errors.append("REVIEW_QUEUE_MANIFEST.json: schema_version must be master_index_review_queue_manifest.v0.")
    if manifest.get("status") not in ALLOWED_MANIFEST_STATUSES:
        errors.append(f"REVIEW_QUEUE_MANIFEST.json: unsupported status {manifest.get('status')!r}.")
    for flag in ["no_runtime_implemented", "no_upload_implemented", "no_accounts_implemented", "no_auto_acceptance"]:
        if manifest.get(flag) is not True:
            errors.append(f"REVIEW_QUEUE_MANIFEST.json: {flag} must be true.")
    for field in ["queue_entries", "decision_files"]:
        value = manifest.get(field)
        if not isinstance(value, list):
            errors.append(f"REVIEW_QUEUE_MANIFEST.json: {field} must be a list.")
            continue
        for rel_path in value:
            if not isinstance(rel_path, str):
                errors.append(f"REVIEW_QUEUE_MANIFEST.json: {field} contains a non-string path.")
                continue
            if _is_unsafe_relative_path(rel_path):
                errors.append(f"REVIEW_QUEUE_MANIFEST.json: {field} contains unsafe path {rel_path!r}.")
            elif not (root / rel_path).exists():
                errors.append(f"{rel_path}: file referenced by {field} is missing.")
    publication = manifest.get("publication_policy")
    if isinstance(publication, Mapping):
        for field in [
            "accepted_public_requires_decision",
            "accepted_public_is_not_rights_clearance",
            "accepted_public_is_not_malware_safety",
            "accepted_public_is_not_canonical_truth",
        ]:
            if publication.get(field) is not True:
                errors.append(f"REVIEW_QUEUE_MANIFEST.json: publication_policy.{field} must be true.")


def _validate_entries(entries: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any] | None, errors: list[str]) -> None:
    seen: set[str] = set()
    expected_queue_id = manifest.get("queue_id") if isinstance(manifest, Mapping) else None
    for index, entry in enumerate(entries, start=1):
        prefix = f"queue_entries.jsonl line {index}"
        missing = REQUIRED_ENTRY_FIELDS - set(entry)
        if missing:
            errors.append(f"{prefix}: missing required fields: {', '.join(sorted(missing))}.")
        if entry.get("schema_version") != "master_index_review_queue_entry.v0":
            errors.append(f"{prefix}: schema_version must be master_index_review_queue_entry.v0.")
        entry_id = entry.get("queue_entry_id")
        if not isinstance(entry_id, str) or not entry_id:
            errors.append(f"{prefix}: queue_entry_id must be a non-empty string.")
        elif entry_id in seen:
            errors.append(f"{prefix}: duplicate queue_entry_id {entry_id!r}.")
        else:
            seen.add(entry_id)
        if expected_queue_id and entry.get("queue_id") != expected_queue_id:
            errors.append(f"{prefix}: queue_id must match REVIEW_QUEUE_MANIFEST.json.")
        _expect_allowed(prefix, "submitted_as_status", entry.get("submitted_as_status"), ALLOWED_PACK_STATUSES, errors)
        _expect_allowed(prefix, "validation_status", entry.get("validation_status"), ALLOWED_VALIDATION_STATUSES, errors)
        _expect_allowed(prefix, "review_status", entry.get("review_status"), ALLOWED_REVIEW_STATUSES, errors)
        _expect_allowed(prefix, "privacy_classification", entry.get("privacy_classification"), ALLOWED_PRIVACY_CLASSES, errors)
        _expect_allowed(prefix, "rights_classification", entry.get("rights_classification"), ALLOWED_RIGHTS_CLASSES, errors)
        _expect_allowed(prefix, "risk_classification", entry.get("risk_classification"), ALLOWED_RISK_CLASSES, errors)
        if entry.get("review_status") == "accepted_public" and not entry.get("decision_ref"):
            errors.append(f"{prefix}: accepted_public review_status requires decision_ref.")
        if entry.get("privacy_classification") == "public_safe":
            _reject_private_paths(entry, f"{prefix}: public_safe entry", errors)
        _validate_pack_ref(prefix, entry.get("contribution_pack_ref"), {"contribution_pack"}, errors)
        for pack_ref in _as_list(entry.get("referenced_packs")):
            _validate_pack_ref(prefix, pack_ref, ALLOWED_PACK_TYPES, errors)
        evidence = entry.get("evidence_summary")
        if isinstance(evidence, Mapping):
            if evidence.get("acceptance_evidence_complete") is True and entry.get("review_status") != "accepted_public":
                errors.append(f"{prefix}: acceptance_evidence_complete=true requires accepted_public review status.")
        else:
            errors.append(f"{prefix}: evidence_summary must be an object.")
        conflict = entry.get("conflict_summary")
        if isinstance(conflict, Mapping):
            status = conflict.get("conflict_status")
            if status not in {"none_detected", "conflict_detected", "disputed", "unknown"}:
                errors.append(f"{prefix}: unsupported conflict_status {status!r}.")
        else:
            errors.append(f"{prefix}: conflict_summary must be an object.")
        limitations = entry.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            errors.append(f"{prefix}: limitations must be a non-empty list.")
        _reject_prohibited_keys(entry, prefix, errors)


def _validate_decisions(
    decisions: Sequence[Mapping[str, Any]],
    entries: Sequence[Mapping[str, Any]],
    errors: list[str],
) -> None:
    entry_ids = {entry.get("queue_entry_id") for entry in entries if isinstance(entry.get("queue_entry_id"), str)}
    seen: set[str] = set()
    for index, decision in enumerate(decisions, start=1):
        prefix = f"review_decisions.jsonl line {index}"
        missing = REQUIRED_DECISION_FIELDS - set(decision)
        if missing:
            errors.append(f"{prefix}: missing required fields: {', '.join(sorted(missing))}.")
        if decision.get("schema_version") != "master_index_review_decision.v0":
            errors.append(f"{prefix}: schema_version must be master_index_review_decision.v0.")
        decision_id = decision.get("decision_id")
        if not isinstance(decision_id, str) or not decision_id:
            errors.append(f"{prefix}: decision_id must be a non-empty string.")
        elif decision_id in seen:
            errors.append(f"{prefix}: duplicate decision_id {decision_id!r}.")
        else:
            seen.add(decision_id)
        if decision.get("queue_entry_id") not in entry_ids:
            errors.append(f"{prefix}: decision references unknown queue_entry_id {decision.get('queue_entry_id')!r}.")
        _expect_allowed(prefix, "decision", decision.get("decision"), ALLOWED_DECISIONS, errors)
        basis_values = _as_list(decision.get("decision_basis"))
        if not basis_values:
            errors.append(f"{prefix}: decision_basis must be a non-empty list.")
        for basis in basis_values:
            if basis not in ALLOWED_DECISION_BASIS:
                errors.append(f"{prefix}: unsupported decision_basis {basis!r}.")
        limitations = decision.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            errors.append(f"{prefix}: limitations must be a non-empty list.")
        claims = decision.get("public_claims_allowed")
        if not isinstance(claims, Mapping):
            errors.append(f"{prefix}: public_claims_allowed must be an object.")
        else:
            for field in ["not_rights_clearance", "not_malware_safety", "not_canonical_truth"]:
                if claims.get(field) is not True:
                    errors.append(f"{prefix}: public_claims_allowed.{field} must be true.")
            if decision.get("decision") == "accept_public":
                if not limitations:
                    errors.append(f"{prefix}: accept_public requires explicit limitations.")
                if claims.get("allowed") is not True:
                    errors.append(f"{prefix}: accept_public requires public_claims_allowed.allowed=true.")
                if not _as_list(claims.get("claims")):
                    errors.append(f"{prefix}: accept_public requires scoped public claims.")
        if decision.get("decision") != "accept_public" and isinstance(claims, Mapping) and claims.get("allowed") is True:
            errors.append(f"{prefix}: non-accept_public decision cannot allow public claims.")
        _reject_private_paths(decision, prefix, errors)
        _reject_prohibited_keys(decision, prefix, errors)


def _validate_pack_ref(prefix: str, value: Any, allowed_types: set[str], errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{prefix}: pack reference must be an object.")
        return
    pack_type = value.get("pack_type")
    if pack_type is not None and pack_type not in allowed_types:
        errors.append(f"{prefix}: unsupported pack_type {pack_type!r}.")
    rel_path = value.get("relative_path")
    if isinstance(rel_path, str) and _is_unsafe_relative_path(rel_path):
        errors.append(f"{prefix}: unsafe referenced pack path {rel_path!r}.")
    _reject_private_paths(value, prefix, errors)
    _reject_prohibited_keys(value, prefix, errors)


def _load_manifest_jsonl_records(root: Path, paths_value: Any, field: str, errors: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not isinstance(paths_value, list):
        return records
    for rel_path in paths_value:
        if not isinstance(rel_path, str):
            continue
        path = root / rel_path
        records.extend(_load_jsonl(path, errors))
    return records


def _validate_checksums(root: Path, *, strict: bool, errors: list[str]) -> dict[str, str]:
    checksum_path = root / "CHECKSUMS.SHA256"
    entries: dict[str, str] = {}
    if not checksum_path.exists():
        return entries
    for line_number, raw_line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: expected '<sha256>  <relative_path>'.")
            continue
        digest, rel_path = parts
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: invalid SHA-256 digest.")
            continue
        if _is_unsafe_relative_path(rel_path):
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: unsafe path {rel_path!r}.")
            continue
        target = root / rel_path
        if not target.exists():
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: {rel_path} does not exist.")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: checksum mismatch for {rel_path}.")
        entries[rel_path] = digest
    for required in REQUIRED_QUEUE_FILES - {"CHECKSUMS.SHA256"}:
        if required not in entries:
            errors.append(f"CHECKSUMS.SHA256: missing checksum for required file {required}.")
    if strict:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.name != "CHECKSUMS.SHA256":
                rel = path.relative_to(root).as_posix()
                if rel not in entries:
                    errors.append(f"CHECKSUMS.SHA256: strict mode missing checksum for {rel}.")
    return entries


def _scan_tree_for_safety(root: Path, errors: list[str]) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        rel = _rel(path)
        if suffix in EXECUTABLE_EXTENSIONS:
            errors.append(f"{rel}: forbidden executable payload extension {suffix}.")
        if suffix in DATABASE_OR_CACHE_EXTENSIONS:
            errors.append(f"{rel}: forbidden raw database/cache extension {suffix}.")
        if suffix in {".json", ".jsonl", ".md", ".txt", ".sha256"} or path.name == "CHECKSUMS.SHA256":
            text = path.read_text(encoding="utf-8")
            lower = text.lower()
            if "http://" in lower or "https://" in lower:
                errors.append(f"{rel}: live URL text is not allowed in the synthetic v0 example queue.")
            for phrase in FORBIDDEN_CLAIM_PHRASES:
                if phrase in lower:
                    errors.append(f"{rel}: forbidden unsupported claim phrase {phrase!r}.")
            for pattern in PRIVATE_PATH_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{rel}: contains a private or absolute local path.")


def _reject_private_paths(value: Any, prefix: str, errors: list[str]) -> None:
    for text in _walk_strings(value):
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(text):
                errors.append(f"{prefix}: contains a private or absolute local path.")
                return


def _reject_prohibited_keys(value: Any, prefix: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key).lower() in PROHIBITED_KEYS:
                errors.append(f"{prefix}: prohibited key {key!r}.")
            _reject_prohibited_keys(nested, prefix, errors)
    elif isinstance(value, list):
        for item in value:
            _reject_prohibited_keys(item, prefix, errors)


def _expect_allowed(prefix: str, field: str, value: Any, allowed: set[str], errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{prefix}: unsupported {field} {value!r}.")


def _is_unsafe_relative_path(rel_path: str) -> bool:
    path = Path(rel_path)
    return path.is_absolute() or any(part == ".." for part in path.parts)


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: JSON parse error at line {exc.lineno}: {exc.msg}.")
    return None


def _load_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: JSONL file is missing.")
        return records
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{_rel(path)} line {line_number}: JSON parse error: {exc.msg}.")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{_rel(path)} line {line_number}: JSONL record must be an object.")
            continue
        records.append(payload)
    return records


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _walk_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, Mapping):
        for key, nested in value.items():
            strings.append(str(key))
            strings.extend(_walk_strings(nested))
    elif isinstance(value, list):
        for item in value:
            strings.extend(_walk_strings(item))
    return strings


def _report(
    root: Path,
    manifest: Mapping[str, Any] | None,
    entries: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_master_index_review_queue",
        "queue_root": _rel(root),
        "queue_id": manifest.get("queue_id") if isinstance(manifest, Mapping) else None,
        "queue_status": manifest.get("status") if isinstance(manifest, Mapping) else None,
        "queue_entry_count": len(entries),
        "decision_count": len(decisions),
        "errors": errors,
        "warnings": warnings,
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Master Index Review Queue v0 validation",
        f"status: {report['status']}",
        f"queue_root: {report['queue_root']}",
        f"queue_id: {report.get('queue_id')}",
        f"queue_entry_count: {report['queue_entry_count']}",
        f"decision_count: {report['decision_count']}",
    ]
    for warning in report.get("warnings", []):
        lines.append(f"warning: {warning}")
    for error in report.get("errors", []):
        lines.append(f"error: {error}")
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
