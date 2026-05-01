from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO

from pack_validator_examples import argument_error, format_all_examples, validate_all_examples


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK_ROOT = REPO_ROOT / "examples" / "evidence_packs" / "minimal_evidence_pack_v0"
EVIDENCE_PACK_SCHEMA = REPO_ROOT / "contracts" / "packs" / "evidence_pack.v0.json"

REQUIRED_FILES = {
    "EVIDENCE_PACK.json",
    "README.md",
    "RIGHTS_AND_ACCESS.md",
    "CHECKSUMS.SHA256",
    "evidence_records.jsonl",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "pack_id",
    "pack_version",
    "title",
    "description",
    "status",
    "producer",
    "privacy",
    "rights_and_access",
    "evidence_files",
    "source_reference_files",
    "checksum_policy",
    "validation",
    "prohibited_contents",
    "notes",
}
ALLOWED_STATUSES = {
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
PUBLIC_LIKE_STATUSES = {"shareable_candidate", "submitted", "accepted_public"}
ALLOWED_PRIVACY_CLASSES = {
    "public_safe",
    "local_private",
    "review_required",
    "restricted",
    "unknown",
}
ALLOWED_RIGHTS_CLASSES = {
    "unknown",
    "public_metadata_only",
    "source_terms_apply",
    "restricted",
    "review_required",
    "not_applicable",
}
ALLOWED_EVIDENCE_KINDS = {
    "source_observation",
    "metadata_claim",
    "compatibility_claim",
    "member_path_claim",
    "checksum_observation",
    "version_observation",
    "release_note_observation",
    "manual_document_observation",
    "review_description_observation",
    "absence_observation",
    "identity_candidate",
    "provenance_note",
    "actionability_note",
}
ALLOWED_CLAIM_TYPES = {
    "describes",
    "mentions",
    "supports_platform",
    "does_not_support_platform",
    "requires_runtime",
    "has_version",
    "latest_known_for_platform",
    "contains_member",
    "has_checksum",
    "documents_hardware",
    "documents_install_step",
    "reports_works_on",
    "reports_failure_on",
    "source_missing",
    "dead_link_observed",
    "archived_trace_exists",
    "same_as_candidate",
    "variant_of_candidate",
    "evidence_for_absence",
    "actionability_hint",
}
ALLOWED_LOCATOR_KINDS = {
    "fixture_locator",
    "source_url_reference",
    "archive_identifier_reference",
    "package_identifier",
    "manual_reference",
    "local_private_reference",
}
REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id",
    "evidence_kind",
    "claim_type",
    "subject_ref",
    "locator",
    "summary",
    "created_by_pack",
    "limitations",
    "privacy_classification",
    "rights_classification",
}
REQUIRED_SOURCE_REFERENCE_FIELDS = {
    "source_ref",
    "label",
    "locator",
    "locator_kind",
    "network_required_to_verify",
    "rights_notes",
    "limitations",
}
REQUIRED_PROHIBITED_CONTENTS = {
    "credentials",
    "api_key",
    "auth_token",
    "password",
    "private_key",
    "private_local_paths",
    "raw_private_files",
    "raw_copyrighted_long_form_text",
    "real_executables",
    "installer_payloads",
    "malware_safety_claims",
    "rights_clearance_claims",
    "live_fetch_authority",
    "master_index_auto_acceptance",
    "canonical_truth_claims",
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
PRIVATE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"\\\\[A-Za-z0-9_.-]+\\"),
    re.compile(r"/(?:Users|home|tmp|var|private)/"),
)
FORBIDDEN_CLAIM_PHRASES = (
    "rights-cleared",
    "rights cleared",
    "malware-free",
    "master index accepted",
    "is canonical truth",
    "claims canonical truth",
    "production-ready",
)
SNIPPET_MAX_CHARS = 500


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an Evidence Pack Contract v0 directory.")
    parser.add_argument("--pack-root", help="Evidence pack directory to validate.")
    parser.add_argument(
        "--all-examples",
        "--known-examples",
        dest="all_examples",
        action="store_true",
        help="Validate all registered evidence pack examples.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Require exact checksum coverage and strict public-safe posture.")
    args = parser.parse_args(argv)

    if args.all_examples and args.pack_root:
        result = argument_error("validate_evidence_pack", "--pack-root cannot be combined with --all-examples.")
    elif args.all_examples:
        result = validate_all_examples(
            pack_type="evidence_pack",
            created_by="validate_evidence_pack",
            root_field="pack_root",
            strict=args.strict,
            validate_one=lambda root: validate_pack(root, strict=args.strict),
        )
    else:
        result = validate_pack(Path(args.pack_root) if args.pack_root else DEFAULT_PACK_ROOT, strict=args.strict)
    if args.json:
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        if result.get("mode") in {"all_examples", "argument_error"}:
            sys.stdout.write(format_all_examples(result, title="Evidence Pack v0 validation", root_field="pack_root"))
        else:
            _print_human(result, sys.stdout)
    return 0 if result["status"] == "valid" else 1


def validate_pack(pack_root: Path, *, strict: bool = False) -> dict[str, Any]:
    pack_root = pack_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    manifest: dict[str, Any] = {}
    evidence_records: list[dict[str, Any]] = []
    source_reference_records: list[dict[str, Any]] = []

    if not EVIDENCE_PACK_SCHEMA.is_file():
        errors.append(f"Missing evidence pack schema: {_rel(EVIDENCE_PACK_SCHEMA)}")
    else:
        try:
            json.loads(EVIDENCE_PACK_SCHEMA.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Evidence pack schema is invalid JSON: {exc}")

    if not pack_root.is_dir():
        errors.append(f"Pack root does not exist or is not a directory: {pack_root}")
        return _result(pack_root, manifest, evidence_records, source_reference_records, errors, warnings)

    for filename in REQUIRED_FILES:
        if not (pack_root / filename).is_file():
            errors.append(f"Missing required file: {filename}")

    manifest_path = pack_root / "EVIDENCE_PACK.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"EVIDENCE_PACK.json is invalid JSON: {exc}")

    if manifest:
        _validate_manifest(manifest, errors, strict=strict)

        for rel_path in manifest.get("evidence_files", []):
            records = _read_jsonl(pack_root / rel_path, errors)
            evidence_records.extend(records)
        for rel_path in manifest.get("source_reference_files", []):
            records = _read_jsonl(pack_root / rel_path, errors)
            source_reference_records.extend(records)

        _validate_evidence_records(manifest, evidence_records, errors, strict=strict)
        _validate_source_references(manifest, source_reference_records, errors, strict=strict)
        _validate_checksums(pack_root, manifest, errors, strict=strict)

    _validate_rights_doc(pack_root, errors)
    _scan_tree_for_safety(pack_root, errors)

    return _result(pack_root, manifest, evidence_records, source_reference_records, errors, warnings)


def _validate_manifest(manifest: Mapping[str, Any], errors: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        errors.append(f"EVIDENCE_PACK.json missing required fields: {', '.join(missing)}")

    if manifest.get("schema_version") != "evidence_pack.v0":
        errors.append("schema_version must be evidence_pack.v0")

    status = manifest.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUSES)}")

    privacy = manifest.get("privacy", {})
    if not isinstance(privacy, Mapping):
        errors.append("privacy must be an object")
        privacy = {}
    classification = privacy.get("classification")
    if classification not in ALLOWED_PRIVACY_CLASSES:
        errors.append(f"privacy.classification must be one of {sorted(ALLOWED_PRIVACY_CLASSES)}")
    if status in PUBLIC_LIKE_STATUSES and classification != "public_safe":
        errors.append("shareable/submitted/accepted_public evidence packs must use privacy.classification=public_safe")
    for flag in ("contains_private_paths", "contains_credentials", "contains_restricted_snippets"):
        if privacy.get(flag) is not False:
            errors.append(f"privacy.{flag} must be false for Evidence Pack v0 public-safe validation")
    if status in PUBLIC_LIKE_STATUSES and privacy.get("local_private_records_allowed") is not False:
        errors.append("shareable/submitted/accepted_public packs must set privacy.local_private_records_allowed=false")

    rights = manifest.get("rights_and_access", {})
    if not isinstance(rights, Mapping):
        errors.append("rights_and_access must be an object")
        rights = {}
    if rights.get("rights_doc") != "RIGHTS_AND_ACCESS.md":
        errors.append("rights_and_access.rights_doc must be RIGHTS_AND_ACCESS.md")
    if rights.get("artifact_distribution_permission") != "not_included":
        errors.append("rights_and_access.artifact_distribution_permission must be not_included for v0 examples")

    if not isinstance(manifest.get("evidence_files"), list) or not manifest.get("evidence_files"):
        errors.append("evidence_files must list at least evidence_records.jsonl")
    elif "evidence_records.jsonl" not in manifest.get("evidence_files", []):
        errors.append("evidence_files must include evidence_records.jsonl")

    checksum_policy = manifest.get("checksum_policy", {})
    if not isinstance(checksum_policy, Mapping):
        errors.append("checksum_policy must be an object")
        checksum_policy = {}
    if checksum_policy.get("algorithm") != "sha256":
        errors.append("checksum_policy.algorithm must be sha256")
    if checksum_policy.get("checksum_file") != "CHECKSUMS.SHA256":
        errors.append("checksum_policy.checksum_file must be CHECKSUMS.SHA256")
    if status in PUBLIC_LIKE_STATUSES and checksum_policy.get("required_for_shareable") is not True:
        errors.append("checksum_policy.required_for_shareable must be true for shareable/submitted packs")

    validation = manifest.get("validation", {})
    if not isinstance(validation, Mapping):
        errors.append("validation must be an object")
        validation = {}
    expected_false = ("no_import_performed", "no_indexing_performed", "no_network_performed", "no_upload_performed")
    for key in expected_false:
        if validation.get(key) is not True:
            errors.append(f"validation.{key} must be true")
    if validation.get("snippet_max_chars") != SNIPPET_MAX_CHARS:
        errors.append(f"validation.snippet_max_chars must be {SNIPPET_MAX_CHARS}")

    prohibited = set(manifest.get("prohibited_contents", []))
    missing_prohibited = sorted(REQUIRED_PROHIBITED_CONTENTS - prohibited)
    if missing_prohibited:
        errors.append(f"prohibited_contents missing required entries: {', '.join(missing_prohibited)}")

    _validate_no_prohibited_keys(manifest, "EVIDENCE_PACK.json", errors)
    if strict and status != "shareable_candidate":
        errors.append("strict validation expects the example evidence pack status to be shareable_candidate")


def _validate_evidence_records(
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    errors: list[str],
    *,
    strict: bool,
) -> None:
    if not records:
        errors.append("At least one evidence record is required")
        return

    status = manifest.get("status")
    seen_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        prefix = f"evidence record {index}"
        missing = sorted(REQUIRED_EVIDENCE_FIELDS - set(record))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")

        evidence_id = record.get("evidence_id")
        if isinstance(evidence_id, str):
            if evidence_id in seen_ids:
                errors.append(f"Duplicate evidence_id: {evidence_id}")
            seen_ids.add(evidence_id)

        if record.get("evidence_kind") not in ALLOWED_EVIDENCE_KINDS:
            errors.append(f"{prefix} has unsupported evidence_kind: {record.get('evidence_kind')}")
        if record.get("claim_type") not in ALLOWED_CLAIM_TYPES:
            errors.append(f"{prefix} has unsupported claim_type: {record.get('claim_type')}")
        if "source_ref" not in record and "source_id" not in record:
            errors.append(f"{prefix} must include source_ref or source_id")

        privacy = record.get("privacy_classification")
        if privacy not in ALLOWED_PRIVACY_CLASSES:
            errors.append(f"{prefix} has unsupported privacy_classification: {privacy}")
        if status in PUBLIC_LIKE_STATUSES and privacy in {"local_private", "restricted", "unknown"}:
            errors.append(f"{prefix} is not public-safe enough for shareable/submitted status")
        if status == "accepted_public" and privacy == "review_required":
            errors.append(f"{prefix} cannot remain review_required in accepted_public status")

        rights = record.get("rights_classification")
        if rights not in ALLOWED_RIGHTS_CLASSES:
            errors.append(f"{prefix} has unsupported rights_classification: {rights}")

        snippet = record.get("snippet")
        if snippet is not None:
            if not isinstance(snippet, str):
                errors.append(f"{prefix} snippet must be a string")
            elif len(snippet) > SNIPPET_MAX_CHARS:
                errors.append(f"{prefix} snippet exceeds {SNIPPET_MAX_CHARS} characters")

        _validate_no_prohibited_keys(record, prefix, errors)
        _validate_text_safety(record, prefix, errors)

    if strict and len(seen_ids) != len(records):
        errors.append("strict validation requires every evidence record to have a unique evidence_id")


def _validate_source_references(
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    errors: list[str],
    *,
    strict: bool,
) -> None:
    if not records and manifest.get("source_reference_files"):
        errors.append("source_reference_files were listed but no source reference records parsed")
    for index, record in enumerate(records, start=1):
        prefix = f"source reference record {index}"
        missing = sorted(REQUIRED_SOURCE_REFERENCE_FIELDS - set(record))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
        if record.get("locator_kind") not in ALLOWED_LOCATOR_KINDS:
            errors.append(f"{prefix} has unsupported locator_kind: {record.get('locator_kind')}")
        if record.get("locator_kind") == "local_private_reference" and manifest.get("status") in PUBLIC_LIKE_STATUSES:
            errors.append(f"{prefix} cannot use local_private_reference in a shareable/submitted pack")
        if record.get("network_required_to_verify") is not False:
            errors.append(f"{prefix} must set network_required_to_verify=false for v0 validation")
        _validate_no_prohibited_keys(record, prefix, errors)
        _validate_text_safety(record, prefix, errors)

    if strict and manifest.get("source_reference_files") and not records:
        errors.append("strict validation requires source reference records when source_reference_files are listed")


def _validate_checksums(pack_root: Path, manifest: Mapping[str, Any], errors: list[str], *, strict: bool) -> None:
    checksum_policy = manifest.get("checksum_policy", {})
    if not isinstance(checksum_policy, Mapping):
        return
    checksum_file = checksum_policy.get("checksum_file", "CHECKSUMS.SHA256")
    checksum_path = pack_root / str(checksum_file)
    if not checksum_path.is_file():
        errors.append("CHECKSUMS.SHA256 is missing")
        return

    expected_paths = [str(path) for path in checksum_policy.get("covers", [])]
    parsed = _read_checksum_file(checksum_path, errors)
    if strict and set(parsed) != set(expected_paths):
        errors.append("CHECKSUMS.SHA256 entries must exactly match checksum_policy.covers in strict mode")
    else:
        missing = sorted(set(expected_paths) - set(parsed))
        if missing:
            errors.append(f"CHECKSUMS.SHA256 missing entries for: {', '.join(missing)}")

    for rel_path in expected_paths:
        path = pack_root / rel_path
        if not path.is_file():
            errors.append(f"Checksummed file is missing: {rel_path}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        expected = parsed.get(rel_path)
        if expected and actual != expected:
            errors.append(f"Checksum mismatch for {rel_path}")


def _read_checksum_file(path: Path, errors: list[str]) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            errors.append(f"Invalid CHECKSUMS.SHA256 line {line_no}")
            continue
        digest, rel_path = parts[0], parts[1].strip()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"Invalid SHA-256 digest on line {line_no}")
        checksums[rel_path] = digest
    return checksums


def _read_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.is_file():
        errors.append(f"JSONL file is missing: {_rel(path)}")
        return records
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{_rel(path)} line {line_no} is invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{_rel(path)} line {line_no} must be a JSON object")
            continue
        records.append(value)
    return records


def _validate_rights_doc(pack_root: Path, errors: list[str]) -> None:
    path = pack_root / "RIGHTS_AND_ACCESS.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8").lower()
    required_phrases = (
        "not rights clearance",
        "not artifact distribution permission",
        "no executable",
        "future public or master-index acceptance would require",
    )
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"RIGHTS_AND_ACCESS.md must mention: {phrase}")


def _scan_tree_for_safety(pack_root: Path, errors: list[str]) -> None:
    for path in pack_root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = _rel(path, pack_root)
        if path.suffix.lower() in EXECUTABLE_EXTENSIONS:
            errors.append(f"File uses forbidden executable/archive payload extension: {rel_path}")
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(text):
                errors.append(f"File appears to contain a private or absolute local path: {rel_path}")
                break
        lowered = text.lower()
        for phrase in FORBIDDEN_CLAIM_PHRASES:
            if phrase in lowered:
                errors.append(f"File appears to contain unsupported claim phrase {phrase!r}: {rel_path}")


def _validate_no_prohibited_keys(value: Any, context: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in PROHIBITED_KEYS:
                errors.append(f"{context} contains prohibited key: {key}")
            _validate_no_prohibited_keys(child, context, errors)
    elif isinstance(value, list):
        for child in value:
            _validate_no_prohibited_keys(child, context, errors)


def _validate_text_safety(value: Any, context: str, errors: list[str]) -> None:
    if isinstance(value, str):
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"{context} contains a private or absolute local path")
                break
        lowered = value.lower()
        for phrase in FORBIDDEN_CLAIM_PHRASES:
            if phrase in lowered:
                errors.append(f"{context} contains unsupported claim phrase: {phrase}")
    elif isinstance(value, Mapping):
        for child in value.values():
            _validate_text_safety(child, context, errors)
    elif isinstance(value, list):
        for child in value:
            _validate_text_safety(child, context, errors)


def _result(
    pack_root: Path,
    manifest: Mapping[str, Any],
    evidence_records: Sequence[Mapping[str, Any]],
    source_reference_records: Sequence[Mapping[str, Any]],
    errors: Sequence[str],
    warnings: Sequence[str],
) -> dict[str, Any]:
    return {
        "created_by": "validate_evidence_pack",
        "status": "invalid" if errors else "valid",
        "pack_root": _rel(pack_root),
        "pack_id": manifest.get("pack_id"),
        "pack_version": manifest.get("pack_version"),
        "pack_status": manifest.get("status"),
        "evidence_record_count": len(evidence_records),
        "source_reference_count": len(source_reference_records),
        "snippet_max_chars": SNIPPET_MAX_CHARS,
        "errors": list(errors),
        "warnings": list(warnings),
    }


def _print_human(result: Mapping[str, Any], stream: TextIO) -> None:
    stream.write("Evidence Pack v0 validation\n")
    stream.write(f"status: {result['status']}\n")
    stream.write(f"pack_root: {result['pack_root']}\n")
    if result.get("pack_id"):
        stream.write(f"pack_id: {result['pack_id']}\n")
    stream.write(f"evidence_record_count: {result['evidence_record_count']}\n")
    if result.get("errors"):
        stream.write("errors:\n")
        for error in result["errors"]:
            stream.write(f"- {error}\n")


def _rel(path: Path, base: Path | None = None) -> str:
    base = base or REPO_ROOT
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
