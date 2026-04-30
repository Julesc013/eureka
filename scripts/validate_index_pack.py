from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK_ROOT = REPO_ROOT / "examples" / "index_packs" / "minimal_index_pack_v0"
INDEX_PACK_SCHEMA = REPO_ROOT / "contracts" / "packs" / "index_pack.v0.json"

REQUIRED_FILES = {
    "INDEX_PACK.json",
    "README.md",
    "PRIVACY_AND_RIGHTS.md",
    "CHECKSUMS.SHA256",
    "index_summary.json",
    "source_coverage.json",
    "record_summaries.jsonl",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "pack_id",
    "pack_version",
    "title",
    "description",
    "status",
    "producer",
    "index_build",
    "source_inventory_reference",
    "schema_versions",
    "index_mode",
    "privacy",
    "rights_and_access",
    "files",
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
ALLOWED_INDEX_MODES = {
    "local_index_only",
    "snapshot_index",
    "source_pack_index",
    "evidence_pack_index",
    "hosted_master_candidate",
}
ALLOWED_INDEX_FORMATS = {
    "summary_only",
    "sqlite_not_included",
    "future_sqlite",
}
ALLOWED_RECORD_KINDS = {
    "source_record",
    "resolved_object",
    "state_or_release",
    "representation",
    "member",
    "synthetic_member",
    "evidence",
    "article_segment",
    "other",
}
REQUIRED_INDEX_BUILD_FIELDS = {
    "index_build_id",
    "index_format",
    "producer_tool",
    "source_count",
    "record_count",
    "deterministic",
    "private_data_included",
    "raw_cache_included",
    "database_included",
}
REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "source_family",
    "coverage_depth",
    "status",
    "record_count",
    "limitations",
    "public_safe",
}
REQUIRED_RECORD_FIELDS = {
    "record_id",
    "record_kind",
    "title",
    "source_id",
    "source_family",
    "public_safe",
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
DATABASE_EXTENSIONS = {
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
    parser = argparse.ArgumentParser(description="Validate a Eureka Index Pack v0 directory.")
    parser.add_argument("--pack-root", default=str(DEFAULT_PACK_ROOT), help="Index pack directory to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require checksum coverage for every pack file.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_index_pack(Path(args.pack_root), strict=args.strict)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_index_pack(pack_root: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    root = pack_root if pack_root.is_absolute() else REPO_ROOT / pack_root
    root = root.resolve()

    if not INDEX_PACK_SCHEMA.exists():
        errors.append(f"{_rel(INDEX_PACK_SCHEMA)}: index pack schema is missing.")
    else:
        _load_json(INDEX_PACK_SCHEMA, errors)

    if not root.is_dir():
        errors.append(f"{_rel(root)}: pack root is missing or not a directory.")
        return _result(root, {}, {}, [], errors, warnings)

    for required in sorted(REQUIRED_FILES):
        if not (root / required).is_file():
            errors.append(f"{required} is required but missing.")

    manifest = _load_json(root / "INDEX_PACK.json", errors)
    if not isinstance(manifest, dict):
        manifest = {}
    index_summary = _load_json(root / "index_summary.json", errors)
    if not isinstance(index_summary, dict):
        index_summary = {}
    source_coverage = _load_json(root / "source_coverage.json", errors)
    if not isinstance(source_coverage, dict):
        source_coverage = {}
    records = _read_jsonl(root / "record_summaries.jsonl", errors)

    _validate_manifest(manifest, errors)
    source_ids = _validate_source_coverage(source_coverage, manifest, errors)
    _validate_record_summaries(records, source_ids, manifest, errors, strict=strict)
    _validate_index_summary(index_summary, manifest, records, source_coverage, errors)
    _validate_optional_files(root, manifest, errors)
    _validate_checksums(root, manifest, errors, strict=strict)
    _validate_privacy_rights_doc(root, errors)
    _scan_tree_for_safety(root, errors)

    if strict:
        listed = _listed_manifest_files(manifest)
        for rel_path in listed:
            if not (root / rel_path).is_file():
                errors.append(f"strict validation listed a missing pack file: {rel_path}")

    return _result(root, manifest, source_coverage, records, errors, warnings)


def _validate_manifest(manifest: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        errors.append(f"INDEX_PACK.json missing required fields: {', '.join(missing)}")

    if manifest.get("schema_version") != "index_pack.v0":
        errors.append("INDEX_PACK.json schema_version must be index_pack.v0")
    if manifest.get("status") not in ALLOWED_STATUSES:
        errors.append(f"INDEX_PACK.json has unsupported status: {manifest.get('status')}")
    if manifest.get("index_mode") not in ALLOWED_INDEX_MODES:
        errors.append(f"INDEX_PACK.json has unsupported index_mode: {manifest.get('index_mode')}")

    build = manifest.get("index_build")
    if not isinstance(build, Mapping):
        errors.append("INDEX_PACK.json index_build must be an object")
    else:
        missing_build = sorted(REQUIRED_INDEX_BUILD_FIELDS - set(build))
        if missing_build:
            errors.append(f"index_build missing required fields: {', '.join(missing_build)}")
        if build.get("index_format") not in ALLOWED_INDEX_FORMATS:
            errors.append(f"index_build has unsupported index_format: {build.get('index_format')}")
        for field in ("private_data_included", "raw_cache_included", "database_included"):
            if build.get(field) is not False:
                errors.append(f"index_build.{field} must be false for v0 public/shareable validation")
        if build.get("deterministic") is not True:
            errors.append("index_build.deterministic must be true for the v0 example posture")

    privacy = manifest.get("privacy")
    status = manifest.get("status")
    if not isinstance(privacy, Mapping):
        errors.append("INDEX_PACK.json privacy must be an object")
    else:
        privacy_class = privacy.get("classification")
        if privacy_class not in ALLOWED_PRIVACY_CLASSES:
            errors.append(f"privacy.classification is unsupported: {privacy_class}")
        if status in PUBLIC_LIKE_STATUSES and privacy_class != "public_safe":
            errors.append("shareable/submitted index packs must use privacy.classification=public_safe in v0")
        for field in (
            "contains_private_paths",
            "contains_credentials",
            "contains_raw_cache",
            "contains_database_files",
            "local_private_records_allowed",
        ):
            if status in PUBLIC_LIKE_STATUSES and privacy.get(field) is not False:
                errors.append(f"privacy.{field} must be false for shareable/submitted index packs")

    validation = manifest.get("validation")
    if isinstance(validation, Mapping):
        for field in (
            "no_import_performed",
            "no_merge_performed",
            "no_network_performed",
            "no_upload_performed",
            "no_database_export_performed",
        ):
            if validation.get(field) is not True:
                errors.append(f"validation.{field} must be true")
    else:
        errors.append("INDEX_PACK.json validation must be an object")

    prohibited = manifest.get("prohibited_contents")
    if isinstance(prohibited, list):
        missing_prohibited = sorted(REQUIRED_PROHIBITED_CONTENTS - {str(item) for item in prohibited})
        if missing_prohibited:
            errors.append(f"prohibited_contents missing required entries: {', '.join(missing_prohibited)}")
    else:
        errors.append("prohibited_contents must be a list")

    _validate_no_prohibited_keys(manifest, "INDEX_PACK.json", errors)
    _validate_text_safety(manifest, "INDEX_PACK.json", errors)


def _validate_source_coverage(
    source_coverage: Mapping[str, Any],
    manifest: Mapping[str, Any],
    errors: list[str],
) -> set[str]:
    sources = source_coverage.get("sources", [])
    if not isinstance(sources, list):
        errors.append("source_coverage.json sources must be a list")
        return set()

    source_ids: set[str] = set()
    for index, source in enumerate(sources, start=1):
        prefix = f"source_coverage source {index}"
        if not isinstance(source, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(REQUIRED_SOURCE_FIELDS - set(source))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
        source_id = source.get("source_id")
        if isinstance(source_id, str):
            if source_id in source_ids:
                errors.append(f"Duplicate source_id in source_coverage.json: {source_id}")
            source_ids.add(source_id)
        if manifest.get("status") in PUBLIC_LIKE_STATUSES and source.get("public_safe") is not True:
            errors.append(f"{prefix} must be public_safe=true for shareable/submitted packs")
        _validate_no_prohibited_keys(source, prefix, errors)
        _validate_text_safety(source, prefix, errors)

    build = manifest.get("index_build")
    if isinstance(build, Mapping) and isinstance(build.get("source_count"), int):
        if build["source_count"] != len(source_ids):
            errors.append("index_build.source_count must match source_coverage unique source count")
    return source_ids


def _validate_record_summaries(
    records: Sequence[Mapping[str, Any]],
    source_ids: set[str],
    manifest: Mapping[str, Any],
    errors: list[str],
    *,
    strict: bool,
) -> None:
    seen_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        prefix = f"record_summaries record {index}"
        missing = sorted(REQUIRED_RECORD_FIELDS - set(record))
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")

        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"{prefix} record_id must be a non-empty string")
        elif record_id in seen_ids:
            errors.append(f"Duplicate record_id: {record_id}")
        else:
            seen_ids.add(record_id)

        record_kind = record.get("record_kind")
        if record_kind not in ALLOWED_RECORD_KINDS:
            errors.append(f"{prefix} has unsupported record_kind: {record_kind}")

        source_id = record.get("source_id")
        if source_id not in source_ids:
            errors.append(f"{prefix} references unknown source_id: {source_id}")

        if manifest.get("status") in PUBLIC_LIKE_STATUSES and record.get("public_safe") is not True:
            errors.append(f"{prefix} must be public_safe=true for shareable/submitted packs")

        member_path = record.get("member_path")
        if isinstance(member_path, str):
            if member_path.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", member_path):
                errors.append(f"{prefix} member_path must be relative and public-safe")

        _validate_no_prohibited_keys(record, prefix, errors)
        _validate_text_safety(record, prefix, errors)

    if strict and len(seen_ids) != len(records):
        errors.append("strict validation requires every record summary to have a unique record_id")

    build = manifest.get("index_build")
    if isinstance(build, Mapping) and isinstance(build.get("record_count"), int):
        if build["record_count"] != len(records):
            errors.append("index_build.record_count must match record_summaries count")


def _validate_index_summary(
    summary: Mapping[str, Any],
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    source_coverage: Mapping[str, Any],
    errors: list[str],
) -> None:
    required = {
        "schema_version",
        "index_build_id",
        "index_mode",
        "record_count",
        "record_kind_counts",
        "source_count",
        "source_family_counts",
        "field_coverage_summary",
        "query_profile_summary",
        "limitations",
        "generated_from",
        "privacy_classification",
    }
    missing = sorted(required - set(summary))
    if missing:
        errors.append(f"index_summary.json missing required fields: {', '.join(missing)}")
    if summary.get("index_mode") != manifest.get("index_mode"):
        errors.append("index_summary.json index_mode must match INDEX_PACK.json index_mode")
    if summary.get("record_count") != len(records):
        errors.append("index_summary.json record_count must match record_summaries count")
    source_count = len(source_coverage.get("sources", [])) if isinstance(source_coverage.get("sources"), list) else None
    if summary.get("source_count") != source_count:
        errors.append("index_summary.json source_count must match source_coverage source count")
    if summary.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSES:
        errors.append("index_summary.json privacy_classification is unsupported")
    _validate_no_prohibited_keys(summary, "index_summary.json", errors)
    _validate_text_safety(summary, "index_summary.json", errors)


def _validate_optional_files(root: Path, manifest: Mapping[str, Any], errors: list[str]) -> None:
    files = manifest.get("files", {})
    if not isinstance(files, Mapping):
        errors.append("INDEX_PACK.json files must be an object")
        return
    for key, rel_path in files.items():
        if not isinstance(rel_path, str):
            errors.append(f"files.{key} must be a string path")
            continue
        path = root / rel_path
        if not path.is_file():
            errors.append(f"files.{key} references a missing file: {rel_path}")
            continue
        if path.suffix == ".json":
            _load_json(path, errors)
        elif path.suffix == ".jsonl":
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
        "not artifact distribution permission",
        "no executable",
        "raw sqlite",
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
        if suffix in DATABASE_EXTENSIONS:
            errors.append(f"File uses forbidden raw database/cache extension: {rel_path}")
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


def _listed_manifest_files(manifest: Mapping[str, Any]) -> set[str]:
    listed = set(REQUIRED_FILES)
    files = manifest.get("files", {})
    if isinstance(files, Mapping):
        for rel_path in files.values():
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
    source_coverage: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    errors: Sequence[str],
    warnings: Sequence[str],
) -> dict[str, Any]:
    sources = source_coverage.get("sources", []) if isinstance(source_coverage, Mapping) else []
    source_count = len(sources) if isinstance(sources, list) else 0
    return {
        "created_by": "validate_index_pack",
        "status": "invalid" if errors else "valid",
        "pack_root": _rel(root),
        "pack_id": manifest.get("pack_id"),
        "pack_version": manifest.get("pack_version"),
        "pack_status": manifest.get("status"),
        "index_mode": manifest.get("index_mode"),
        "source_count": source_count,
        "record_count": len(records),
        "errors": list(errors),
        "warnings": list(warnings),
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Index Pack v0 validation",
        f"status: {report['status']}",
        f"pack_root: {report['pack_root']}",
    ]
    if report.get("pack_id"):
        lines.append(f"pack_id: {report['pack_id']}")
    lines.append(f"source_count: {report['source_count']}")
    lines.append(f"record_count: {report['record_count']}")
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
