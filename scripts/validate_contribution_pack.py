from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK_ROOT = REPO_ROOT / "examples" / "contribution_packs" / "minimal_contribution_pack_v0"
CONTRIBUTION_PACK_SCHEMA = REPO_ROOT / "contracts" / "packs" / "contribution_pack.v0.json"

REQUIRED_FILES = {
    "CONTRIBUTION_PACK.json",
    "README.md",
    "PRIVACY_AND_RIGHTS.md",
    "CHECKSUMS.SHA256",
    "contribution_items.jsonl",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "pack_id",
    "pack_version",
    "title",
    "description",
    "status",
    "producer",
    "contribution_scope",
    "contribution_item_files",
    "referenced_packs",
    "privacy",
    "rights_and_access",
    "review_requirements",
    "checksum_policy",
    "validation",
    "prohibited_contents",
    "notes",
}
REQUIRED_CONTRIBUTION_FIELDS = {
    "contribution_id",
    "contribution_type",
    "summary",
    "proposed_action",
    "evidence_refs",
    "privacy_classification",
    "rights_classification",
    "review_status",
    "limitations",
    "created_by_pack",
}
REQUIRED_PACK_REF_FIELDS = {
    "pack_ref",
    "pack_type",
    "pack_id",
    "pack_version",
    "validation_status",
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
ALLOWED_CONTRIBUTION_TYPES = {
    "source_record_candidate",
    "evidence_record_candidate",
    "index_coverage_candidate",
    "manual_observation",
    "metadata_correction",
    "alias_suggestion",
    "compatibility_suggestion",
    "member_path_suggestion",
    "checksum_observation",
    "absence_report",
    "dead_link_report",
    "result_quality_feedback",
    "source_coverage_report",
    "duplicate_or_identity_candidate",
    "documentation_hint",
    "review_note",
}
ALLOWED_PROPOSED_ACTIONS = {
    "add_candidate",
    "update_candidate",
    "deprecate_candidate",
    "mark_review_required",
    "link_existing_records",
    "split_identity_candidate",
    "merge_identity_candidate_for_review",
    "add_absence_evidence",
    "add_compatibility_evidence",
    "add_member_path_evidence",
    "add_alias_candidate",
    "no_action_note",
}
ALLOWED_REVIEW_STATUSES = {
    "pending",
    "review_required",
    "quarantined",
    "accepted_public",
    "rejected",
    "redacted",
}
ALLOWED_PACK_TYPES = {"source_pack", "evidence_pack", "index_pack"}
ALLOWED_OBSERVATION_STATUSES = {"pending", "observed", "invalid", "redacted"}
REQUIRED_PROHIBITED_CONTENTS = {
    "credentials",
    "api_key",
    "auth_token",
    "password",
    "private_key",
    "private_local_paths",
    "raw_private_files",
    "raw_cache_export",
    "raw_sqlite_database",
    "raw_copyrighted_long_form_text",
    "real_executables",
    "installer_payloads",
    "binary_blobs",
    "download_install_urls",
    "malware_safety_claims",
    "rights_clearance_claims",
    "live_fetch_authority",
    "master_index_auto_acceptance",
    "canonical_truth_claims",
    "accounts_or_identity",
    "telemetry_payloads",
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
DATABASE_OR_CACHE_EXTENSIONS = {
    ".cache",
    ".db",
    ".sqlite",
    ".sqlite3",
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
    re.compile(r"\b[A-Za-z]:[\\/][^\s\"']+"),
    re.compile(r"(^|[\s\"'])(/Users|/home|/tmp|/var|/etc)/[^\s\"']+"),
    re.compile(r"\\\\[^\\\s]+\\[^\\\s]+"),
)
FORBIDDEN_CLAIM_PHRASES = (
    "rights-cleared",
    "rights cleared",
    "malware-free",
    "malware safe to run",
    "accepted by the master index",
    "is canonical proof",
    "claims canonical truth",
    "production-ready",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Eureka Contribution Pack v0 directory.")
    parser.add_argument("--pack-root", default=str(DEFAULT_PACK_ROOT), help="Contribution pack directory to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require checksum coverage for every pack file.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_contribution_pack(Path(args.pack_root), strict=args.strict)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_contribution_pack(pack_root: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    root = pack_root if pack_root.is_absolute() else REPO_ROOT / pack_root
    root = root.resolve()

    if not CONTRIBUTION_PACK_SCHEMA.exists():
        errors.append(f"{_rel(CONTRIBUTION_PACK_SCHEMA)}: contribution pack schema is missing.")
    else:
        _load_json(CONTRIBUTION_PACK_SCHEMA, errors)

    if not root.is_dir():
        errors.append(f"{_rel(root)}: pack root is missing or not a directory.")
        return _result(root, {}, [], [], errors, warnings)

    for required in sorted(REQUIRED_FILES):
        if not (root / required).is_file():
            errors.append(f"{required} is required but missing.")

    manifest = _load_json(root / "CONTRIBUTION_PACK.json", errors)
    if not isinstance(manifest, dict):
        manifest = {}

    item_records = _read_jsonl(root / "contribution_items.jsonl", errors)
    pack_refs = _load_pack_refs(root, manifest, errors)
    manual_observations = _read_optional_jsonl(root / "manual_observations.jsonl", errors)

    _validate_manifest(manifest, root, errors)
    _validate_contribution_items(item_records, manifest, errors)
    _validate_pack_refs(pack_refs, errors)
    _validate_manual_observations(manual_observations, manifest, errors)
    _validate_optional_jsonl_files(root, errors)
    _validate_checksums(root, manifest, errors, strict=strict)
    _validate_privacy_rights_doc(root, errors)
    _scan_tree_for_safety(root, errors)

    if strict:
        listed = _listed_manifest_files(manifest)
        for rel_path in listed:
            if not (root / rel_path).is_file():
                errors.append(f"strict validation listed a missing pack file: {rel_path}")

    return _result(root, manifest, item_records, manual_observations, errors, warnings)


def _validate_manifest(manifest: Mapping[str, Any], root: Path, errors: list[str]) -> None:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        errors.append(f"CONTRIBUTION_PACK.json missing required fields: {', '.join(missing)}")

    if manifest.get("schema_version") != "contribution_pack.v0":
        errors.append("CONTRIBUTION_PACK.json schema_version must be contribution_pack.v0")
    if manifest.get("status") not in ALLOWED_STATUSES:
        errors.append(f"CONTRIBUTION_PACK.json has unsupported status: {manifest.get('status')}")

    scope = manifest.get("contribution_scope")
    if not isinstance(scope, Mapping):
        errors.append("CONTRIBUTION_PACK.json contribution_scope must be an object")
    else:
        types = scope.get("contribution_types", [])
        if not isinstance(types, list) or not types:
            errors.append("contribution_scope.contribution_types must be a non-empty list")
        else:
            for contribution_type in types:
                if contribution_type not in ALLOWED_CONTRIBUTION_TYPES:
                    errors.append(f"contribution_scope has unsupported contribution_type: {contribution_type}")
        if scope.get("mutation_authority") != "review_candidate_only":
            errors.append("contribution_scope.mutation_authority must be review_candidate_only")

    item_files = manifest.get("contribution_item_files")
    if not isinstance(item_files, list) or "contribution_items.jsonl" not in item_files:
        errors.append("contribution_item_files must include contribution_items.jsonl")
    elif any(not isinstance(path, str) for path in item_files):
        errors.append("contribution_item_files entries must be string paths")
    else:
        for rel_path in item_files:
            if not (root / rel_path).is_file():
                errors.append(f"contribution_item_files references a missing file: {rel_path}")

    refs = manifest.get("referenced_packs")
    if not isinstance(refs, Mapping):
        errors.append("CONTRIBUTION_PACK.json referenced_packs must be an object")
    else:
        if refs.get("embedded_packs") is not False:
            errors.append("referenced_packs.embedded_packs must be false in v0")
        for key in ("source_pack_refs_file", "evidence_pack_refs_file", "index_pack_refs_file"):
            rel_path = refs.get(key)
            if rel_path is not None and not isinstance(rel_path, str):
                errors.append(f"referenced_packs.{key} must be a string or null")
            elif isinstance(rel_path, str) and not (root / rel_path).is_file():
                errors.append(f"referenced_packs.{key} references a missing file: {rel_path}")

    _validate_privacy(manifest, errors)
    _validate_rights_and_review(manifest, errors)

    validation = manifest.get("validation")
    if isinstance(validation, Mapping):
        for field in (
            "no_upload_performed",
            "no_import_performed",
            "no_review_queue_runtime",
            "no_network_performed",
            "no_automatic_acceptance",
        ):
            if validation.get(field) is not True:
                errors.append(f"validation.{field} must be true")
    else:
        errors.append("CONTRIBUTION_PACK.json validation must be an object")

    prohibited = manifest.get("prohibited_contents")
    if isinstance(prohibited, list):
        missing_prohibited = sorted(REQUIRED_PROHIBITED_CONTENTS - {str(item) for item in prohibited})
        if missing_prohibited:
            errors.append(f"prohibited_contents missing required entries: {', '.join(missing_prohibited)}")
    else:
        errors.append("prohibited_contents must be a list")

    _validate_no_prohibited_keys(manifest, "CONTRIBUTION_PACK.json", errors)
    _validate_text_safety(manifest, "CONTRIBUTION_PACK.json", errors)


def _validate_privacy(manifest: Mapping[str, Any], errors: list[str]) -> None:
    privacy = manifest.get("privacy")
    status = manifest.get("status")
    if not isinstance(privacy, Mapping):
        errors.append("CONTRIBUTION_PACK.json privacy must be an object")
        return
    privacy_class = privacy.get("classification")
    if privacy_class not in ALLOWED_PRIVACY_CLASSES:
        errors.append(f"privacy.classification is unsupported: {privacy_class}")
    if status in PUBLIC_LIKE_STATUSES and privacy_class != "public_safe":
        errors.append("shareable/submitted contribution packs must use privacy.classification=public_safe in v0")
    for field in (
        "contains_private_paths",
        "contains_credentials",
        "contains_raw_cache",
        "contains_database_files",
        "contains_executables",
        "contains_unreviewed_external_observations",
        "local_private_records_allowed",
    ):
        if status in PUBLIC_LIKE_STATUSES and privacy.get(field) is not False:
            errors.append(f"privacy.{field} must be false for shareable/submitted contribution packs")


def _validate_rights_and_review(manifest: Mapping[str, Any], errors: list[str]) -> None:
    rights = manifest.get("rights_and_access")
    if not isinstance(rights, Mapping):
        errors.append("CONTRIBUTION_PACK.json rights_and_access must be an object")
    else:
        for field in ("not_rights_clearance", "not_malware_safety", "not_canonical_truth"):
            if rights.get(field) is not True:
                errors.append(f"rights_and_access.{field} must be true")
        for field in ("raw_binaries_included", "long_copyrighted_text_included"):
            if rights.get(field) is not False:
                errors.append(f"rights_and_access.{field} must be false")

    review = manifest.get("review_requirements")
    if not isinstance(review, Mapping):
        errors.append("CONTRIBUTION_PACK.json review_requirements must be an object")
    else:
        for field in (
            "human_review_required",
            "master_index_acceptance_requires_review",
            "no_automatic_acceptance",
        ):
            if review.get(field) is not True:
                errors.append(f"review_requirements.{field} must be true")
        if review.get("review_queue_runtime_implemented") is not False:
            errors.append("review_requirements.review_queue_runtime_implemented must be false")


def _validate_contribution_items(
    records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    errors: list[str],
) -> None:
    seen_ids: set[str] = set()
    created_by_pack = manifest.get("pack_id")
    for index, record in enumerate(records, start=1):
        prefix = f"contribution_items record {index}"
        missing = sorted(REQUIRED_CONTRIBUTION_FIELDS - set(record))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")

        contribution_id = record.get("contribution_id")
        if not isinstance(contribution_id, str) or not contribution_id:
            errors.append(f"{prefix} contribution_id must be a non-empty string")
        elif contribution_id in seen_ids:
            errors.append(f"Duplicate contribution_id: {contribution_id}")
        else:
            seen_ids.add(contribution_id)

        if record.get("contribution_type") not in ALLOWED_CONTRIBUTION_TYPES:
            errors.append(f"{prefix} has unsupported contribution_type: {record.get('contribution_type')}")
        if record.get("proposed_action") not in ALLOWED_PROPOSED_ACTIONS:
            errors.append(f"{prefix} has unsupported proposed_action: {record.get('proposed_action')}")
        if record.get("review_status") not in ALLOWED_REVIEW_STATUSES:
            errors.append(f"{prefix} has unsupported review_status: {record.get('review_status')}")
        if record.get("created_by_pack") != created_by_pack:
            errors.append(f"{prefix} created_by_pack must match CONTRIBUTION_PACK.json pack_id")

        evidence_refs = record.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append(f"{prefix} evidence_refs must be a list")
        limitations = record.get("limitations")
        if not isinstance(limitations, list):
            errors.append(f"{prefix} limitations must be a list")

        if manifest.get("status") in PUBLIC_LIKE_STATUSES:
            if record.get("privacy_classification") != "public_safe":
                errors.append(f"{prefix} must use privacy_classification=public_safe for shareable/submitted packs")
            if record.get("review_status") == "accepted_public":
                errors.append(f"{prefix} must not be accepted_public before a future review queue exists")

        _validate_no_prohibited_keys(record, prefix, errors)
        _validate_text_safety(record, prefix, errors)


def _load_pack_refs(root: Path, manifest: Mapping[str, Any], errors: list[str]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    referenced = manifest.get("referenced_packs", {})
    if not isinstance(referenced, Mapping):
        return refs
    for key in ("source_pack_refs_file", "evidence_pack_refs_file", "index_pack_refs_file"):
        rel_path = referenced.get(key)
        if isinstance(rel_path, str):
            refs.extend(_read_jsonl(root / rel_path, errors))
    return refs


def _validate_pack_refs(records: Sequence[Mapping[str, Any]], errors: list[str]) -> None:
    seen_refs: set[str] = set()
    for index, record in enumerate(records, start=1):
        prefix = f"pack reference {index}"
        missing = sorted(REQUIRED_PACK_REF_FIELDS - set(record))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
        pack_ref = record.get("pack_ref")
        if not isinstance(pack_ref, str) or not pack_ref:
            errors.append(f"{prefix} pack_ref must be a non-empty string")
        elif pack_ref in seen_refs:
            errors.append(f"Duplicate pack_ref: {pack_ref}")
        else:
            seen_refs.add(pack_ref)
        if record.get("pack_type") not in ALLOWED_PACK_TYPES:
            errors.append(f"{prefix} has unsupported pack_type: {record.get('pack_type')}")
        rel_path = record.get("relative_path")
        if isinstance(rel_path, str) and (rel_path.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", rel_path)):
            errors.append(f"{prefix} relative_path must be relative")
        _validate_no_prohibited_keys(record, prefix, errors)
        _validate_text_safety(record, prefix, errors)


def _validate_manual_observations(
    records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    errors: list[str],
) -> None:
    required = {"observation_id", "system_id", "query_id", "observation_status", "summary"}
    seen_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        prefix = f"manual observation {index}"
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
        observation_id = record.get("observation_id")
        if isinstance(observation_id, str):
            if observation_id in seen_ids:
                errors.append(f"Duplicate observation_id: {observation_id}")
            seen_ids.add(observation_id)
        else:
            errors.append(f"{prefix} observation_id must be a string")
        status = record.get("observation_status")
        if status not in ALLOWED_OBSERVATION_STATUSES:
            errors.append(f"{prefix} has unsupported observation_status: {status}")
        if status == "observed":
            if not record.get("observed_at") or not record.get("operator") or not record.get("result_refs"):
                errors.append(f"{prefix} observed manual observation must include observed_at, operator, and result_refs")
            system_id = str(record.get("system_id", "")).lower()
            summary = str(record.get("summary", "")).lower()
            if "synthetic" in system_id or "example" in system_id or "fake" in summary or "synthetic" in summary:
                errors.append(f"{prefix} appears to mark a synthetic or fake observation as observed")
        if status == "observed" and manifest.get("privacy", {}).get("contains_unreviewed_external_observations") is False:
            errors.append(f"{prefix} cannot be observed when manifest says no unreviewed external observations are present")
        _validate_no_prohibited_keys(record, prefix, errors)
        _validate_text_safety(record, prefix, errors)


def _validate_optional_jsonl_files(root: Path, errors: list[str]) -> None:
    known = {
        "alias_suggestions.jsonl",
        "absence_reports.jsonl",
        "metadata_corrections.jsonl",
        "compatibility_suggestions.jsonl",
        "member_path_suggestions.jsonl",
        "result_feedback.jsonl",
        "review_notes.jsonl",
        "index_pack_refs.jsonl",
    }
    for name in sorted(known):
        path = root / name
        if path.is_file():
            _read_jsonl(path, errors)


def _validate_checksums(root: Path, manifest: Mapping[str, Any], errors: list[str], *, strict: bool) -> None:
    checksum_policy = manifest.get("checksum_policy", {})
    if not isinstance(checksum_policy, Mapping):
        errors.append("checksum_policy must be an object")
        return
    checksum_file = checksum_policy.get("checksum_file", "CHECKSUMS.SHA256")
    checksum_path = root / str(checksum_file)
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
        path = root / rel_path
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


def _read_optional_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return _read_jsonl(path, errors)


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


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"JSON file is missing: {_rel(path)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)} is invalid JSON: {exc}")
        return {}


def _validate_privacy_rights_doc(root: Path, errors: list[str]) -> None:
    path = root / "PRIVACY_AND_RIGHTS.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8").lower()
    required_phrases = (
        "not rights clearance",
        "not malware safety",
        "not canonical truth",
        "no executable",
        "future public or master-index acceptance would require",
    )
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"PRIVACY_AND_RIGHTS.md must mention: {phrase}")


def _scan_tree_for_safety(root: Path, errors: list[str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = _rel(path, root)
        suffix = path.suffix.lower()
        if suffix in EXECUTABLE_EXTENSIONS:
            errors.append(f"File uses forbidden executable payload extension: {rel_path}")
        if suffix in DATABASE_OR_CACHE_EXTENSIONS:
            errors.append(f"File uses forbidden raw database/cache extension: {rel_path}")
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "http://" in text.lower() or "https://" in text.lower():
            errors.append(f"File appears to contain live network locator text: {rel_path}")
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


def _listed_manifest_files(manifest: Mapping[str, Any]) -> set[str]:
    listed = set(REQUIRED_FILES)
    for rel_path in manifest.get("contribution_item_files", []):
        if isinstance(rel_path, str):
            listed.add(rel_path)
    referenced = manifest.get("referenced_packs", {})
    if isinstance(referenced, Mapping):
        for rel_path in referenced.values():
            if isinstance(rel_path, str):
                listed.add(rel_path)
    checksum_policy = manifest.get("checksum_policy", {})
    if isinstance(checksum_policy, Mapping):
        for rel_path in checksum_policy.get("covers", []):
            if isinstance(rel_path, str):
                listed.add(rel_path)
    return listed


def _result(
    root: Path,
    manifest: Mapping[str, Any],
    item_records: Sequence[Mapping[str, Any]],
    manual_observations: Sequence[Mapping[str, Any]],
    errors: Sequence[str],
    warnings: Sequence[str],
) -> dict[str, Any]:
    return {
        "created_by": "validate_contribution_pack",
        "status": "invalid" if errors else "valid",
        "pack_root": _rel(root),
        "pack_id": manifest.get("pack_id"),
        "pack_version": manifest.get("pack_version"),
        "pack_status": manifest.get("status"),
        "contribution_item_count": len(item_records),
        "manual_observation_count": len(manual_observations),
        "errors": list(errors),
        "warnings": list(warnings),
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Contribution Pack v0 validation",
        f"status: {report['status']}",
        f"pack_root: {report['pack_root']}",
    ]
    if report.get("pack_id"):
        lines.append(f"pack_id: {report['pack_id']}")
    lines.append(f"contribution_item_count: {report['contribution_item_count']}")
    lines.append(f"manual_observation_count: {report['manual_observation_count']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _rel(path: Path, base: Path | None = None) -> str:
    base = base or REPO_ROOT
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
