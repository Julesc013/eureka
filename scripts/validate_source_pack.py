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
DEFAULT_PACK_ROOT = REPO_ROOT / "examples" / "source_packs" / "minimal_recorded_source_pack_v0"
SOURCE_PACK_SCHEMA = REPO_ROOT / "contracts" / "packs" / "source_pack.v0.json"

REQUIRED_FILES = {
    "SOURCE_PACK.json",
    "README.md",
    "RIGHTS_AND_ACCESS.md",
    "CHECKSUMS.SHA256",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "pack_id",
    "pack_version",
    "title",
    "description",
    "status",
    "producer",
    "source_families",
    "source_records",
    "evidence_files",
    "fixture_files",
    "rights_and_access",
    "privacy",
    "capabilities",
    "prohibited_behaviors",
    "checksums",
    "validation",
    "notes",
}
ALLOWED_STATUSES = {
    "draft",
    "local_private",
    "shareable_candidate",
    "submitted",
    "accepted_public",
    "rejected",
    "superseded",
}
PUBLIC_LIKE_STATUSES = {"shareable_candidate", "submitted", "accepted_public"}
REQUIRED_PROHIBITED_BEHAVIORS = {
    "live_network_fetch",
    "arbitrary_url_fetch",
    "scraping",
    "crawling",
    "executable_payloads",
    "installer_payloads",
    "downloads",
    "uploads",
    "credential_submission",
    "private_path_publication",
    "raw_private_file_export",
    "malware_safety_claim",
    "rights_clearance_claim",
    "master_index_auto_acceptance",
    "runtime_plugin_execution",
}
REQUIRED_SOURCE_RECORD_FIELDS = {
    "source_id",
    "source_family",
    "label",
    "posture",
    "coverage_depth",
    "connector_mode",
    "capabilities",
    "limitations",
    "next_coverage_step",
    "rights_and_access",
    "fixture_backed",
    "live_supported",
    "network_required",
}
REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id",
    "source_id",
    "subject_ref",
    "evidence_kind",
    "claim_type",
    "summary",
    "locator",
    "created_by_pack",
    "limitations",
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
    ".zip",
}
PROHIBITED_KEYS = {
    "api_key",
    "auth_token",
    "credential",
    "credentials",
    "password",
    "secret",
    "source_credentials",
    "token",
}
FORBIDDEN_CLAIM_PHRASES = (
    "rights-cleared",
    "rights cleared",
    "malware safe to run",
    "malware-free",
    "production plugin",
    "master index accepted",
    "live connector implemented",
)
PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/][^\s\"']+"),
    re.compile(r"(^|[\s\"'])(/Users|/home|/tmp|/var|/etc)/[^\s\"']+"),
    re.compile(r"\\\\[^\\\s]+\\[^\\\s]+"),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Eureka Source Pack v0 directory.")
    parser.add_argument("--pack-root", help="Source pack directory to validate.")
    parser.add_argument(
        "--all-examples",
        "--known-examples",
        dest="all_examples",
        action="store_true",
        help="Validate all registered source pack examples.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require checksum coverage for every pack file.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.all_examples and args.pack_root:
        report = argument_error("validate_source_pack", "--pack-root cannot be combined with --all-examples.")
    elif args.all_examples:
        report = validate_all_examples(
            pack_type="source_pack",
            created_by="validate_source_pack",
            root_field="pack_root",
            strict=args.strict,
            validate_one=lambda root: validate_source_pack(root, strict=args.strict),
        )
    else:
        report = validate_source_pack(Path(args.pack_root) if args.pack_root else DEFAULT_PACK_ROOT, strict=args.strict)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        if report.get("mode") in {"all_examples", "argument_error"}:
            output.write(format_all_examples(report, title="Source Pack v0 validation", root_field="pack_root"))
        else:
            output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_source_pack(pack_root: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    root = pack_root if pack_root.is_absolute() else REPO_ROOT / pack_root
    root = root.resolve()

    if not SOURCE_PACK_SCHEMA.exists():
        errors.append(f"{_rel(SOURCE_PACK_SCHEMA)}: source pack schema is missing.")
    else:
        _load_json(SOURCE_PACK_SCHEMA, errors)

    if not root.exists() or not root.is_dir():
        errors.append(f"{_display_path(root)}: source pack directory is missing.")
        return _report(root, None, [], errors, warnings)

    for filename in sorted(REQUIRED_FILES):
        if not (root / filename).is_file():
            errors.append(f"{_display_path(root / filename)}: required pack file is missing.")

    manifest = _load_json(root / "SOURCE_PACK.json", errors)
    source_records: list[Mapping[str, Any]] = []
    evidence_records: list[Mapping[str, Any]] = []
    representation_records: list[Mapping[str, Any]] = []

    if isinstance(manifest, Mapping):
        _validate_manifest(root, manifest, errors)
        source_records = _validate_source_records(root, manifest, errors)
        evidence_records = _validate_evidence_records(root, manifest, errors)
        representation_records = _validate_jsonl_files(
            root,
            _string_list(manifest.get("representation_files")),
            "representation",
            errors,
        )
        _validate_fixture_files(root, manifest, errors)
        _validate_checksums(root, manifest, strict=strict, errors=errors)
        _validate_pack_safety(root, manifest, source_records + evidence_records + representation_records, errors)
        _validate_docs(root, errors)

    return _report(root, manifest, source_records, errors, warnings)


def _validate_manifest(root: Path, manifest: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    for key in missing:
        errors.append("SOURCE_PACK.json: missing required field " + key + ".")

    if manifest.get("schema_version") != "source_pack.v0":
        errors.append("SOURCE_PACK.json: schema_version must be source_pack.v0.")
    if manifest.get("status") not in ALLOWED_STATUSES:
        errors.append("SOURCE_PACK.json: status is not a Source Pack v0 status.")
    if manifest.get("status") == "accepted_public":
        errors.append("SOURCE_PACK.json: accepted_public requires a future master-index review path, not v0 example validation.")

    source_families = _string_list(manifest.get("source_families"))
    if not source_families:
        errors.append("SOURCE_PACK.json: source_families must be a non-empty array.")

    privacy = _mapping(manifest.get("privacy"))
    status = manifest.get("status")
    if status in PUBLIC_LIKE_STATUSES and privacy.get("classification") != "public_safe":
        errors.append("SOURCE_PACK.json: public/shareable statuses require privacy.classification public_safe.")
    for flag in ("contains_private_paths", "contains_credentials", "contains_raw_private_files"):
        if privacy.get(flag) is not False:
            errors.append(f"SOURCE_PACK.json: privacy.{flag} must be false for the v0 example/public-safe pack.")

    capabilities = _mapping(manifest.get("capabilities"))
    false_required = {
        "network_required",
        "live_supported",
        "allows_executables",
        "allows_upload",
        "allows_arbitrary_local_paths",
        "import_implemented",
        "indexing_implemented",
    }
    for key in false_required:
        if capabilities.get(key) is not False:
            errors.append(f"SOURCE_PACK.json: capabilities.{key} must be false.")
    if capabilities.get("fixture_backed") is not True:
        errors.append("SOURCE_PACK.json: capabilities.fixture_backed must be true for the example pack.")

    prohibited = set(_string_list(manifest.get("prohibited_behaviors")))
    missing_prohibited = sorted(REQUIRED_PROHIBITED_BEHAVIORS - prohibited)
    if missing_prohibited:
        errors.append("SOURCE_PACK.json: prohibited_behaviors missing " + ", ".join(missing_prohibited) + ".")

    validation = _mapping(manifest.get("validation"))
    if validation.get("no_import_performed") is not True:
        errors.append("SOURCE_PACK.json: validation.no_import_performed must be true.")
    if validation.get("no_network_performed") is not True:
        errors.append("SOURCE_PACK.json: validation.no_network_performed must be true.")

    rights = _mapping(manifest.get("rights_and_access"))
    rights_doc = rights.get("document")
    if not isinstance(rights_doc, str) or not _safe_child(root, rights_doc).is_file():
        errors.append("SOURCE_PACK.json: rights_and_access.document must point to an existing pack file.")
    if rights.get("malware_scan_status") not in {"not_applicable", "not_scanned", "future"}:
        errors.append("SOURCE_PACK.json: rights_and_access.malware_scan_status has invalid value.")


def _validate_source_records(root: Path, manifest: Mapping[str, Any], errors: list[str]) -> list[Mapping[str, Any]]:
    source_records_decl = _mapping(manifest.get("source_records"))
    files = _string_list(source_records_decl.get("files"))
    if source_records_decl.get("mode") not in {"file", "inline", "file_and_inline"}:
        errors.append("SOURCE_PACK.json: source_records.mode must be file, inline, or file_and_inline.")
    records = _validate_jsonl_files(root, files, "source", errors)
    inline = source_records_decl.get("records")
    if isinstance(inline, list):
        records.extend(item for item in inline if isinstance(item, Mapping))
    if not records:
        errors.append("source_records: at least one source record is required.")

    source_families = set(_string_list(manifest.get("source_families")))
    for record in records:
        missing = sorted(REQUIRED_SOURCE_RECORD_FIELDS - set(record))
        for key in missing:
            errors.append(f"source_records: {record.get('source_id', '<unknown>')} missing {key}.")
        if record.get("source_family") not in source_families:
            errors.append(f"source_records: {record.get('source_id')} source_family is not declared in manifest.")
        for flag in ("live_supported", "network_required"):
            if record.get(flag) is not False:
                errors.append(f"source_records: {record.get('source_id')} {flag} must be false.")
        if record.get("fixture_backed") is not True:
            errors.append(f"source_records: {record.get('source_id')} fixture_backed must be true.")
        capabilities = _mapping(record.get("capabilities"))
        for flag in ("supports_live_probe", "network_required", "live_supported"):
            if capabilities.get(flag) is not False:
                errors.append(f"source_records: {record.get('source_id')} capabilities.{flag} must be false.")
    return records


def _validate_evidence_records(root: Path, manifest: Mapping[str, Any], errors: list[str]) -> list[Mapping[str, Any]]:
    records = _validate_jsonl_files(root, _string_list(manifest.get("evidence_files")), "evidence", errors)
    if not records:
        errors.append("evidence_files: at least one evidence record is required.")
    source_ids = {record.get("source_id") for record in _validate_source_records_for_ids(root, manifest)}
    for record in records:
        missing = sorted(REQUIRED_EVIDENCE_FIELDS - set(record))
        for key in missing:
            errors.append(f"evidence_records: {record.get('evidence_id', '<unknown>')} missing {key}.")
        if record.get("source_id") not in source_ids:
            errors.append(f"evidence_records: {record.get('evidence_id')} references unknown source_id.")
        if not isinstance(record.get("limitations"), list) or not record.get("limitations"):
            errors.append(f"evidence_records: {record.get('evidence_id')} must include limitations.")
    return records


def _validate_source_records_for_ids(root: Path, manifest: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    files = _string_list(_mapping(manifest.get("source_records")).get("files"))
    for rel_path in files:
        path = _safe_child(root, rel_path)
        if not path.is_file():
            continue
        for item in _load_jsonl_silent(path):
            if isinstance(item, Mapping):
                records.append(item)
    return records


def _validate_fixture_files(root: Path, manifest: Mapping[str, Any], errors: list[str]) -> None:
    fixtures = _string_list(manifest.get("fixture_files"))
    if not fixtures:
        errors.append("SOURCE_PACK.json: fixture_files must list at least one tiny deterministic fixture.")
    for rel_path in fixtures:
        path = _safe_child(root, rel_path)
        if not path.is_file():
            errors.append(f"{rel_path}: declared fixture file is missing.")


def _validate_checksums(root: Path, manifest: Mapping[str, Any], *, strict: bool, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.is_file():
        return
    checksums = _parse_checksums(checksum_path, errors)
    declared = set(_string_list(_mapping(manifest.get("checksums")).get("covers")))
    if not declared:
        errors.append("SOURCE_PACK.json: checksums.covers must list pack files.")
    missing_from_checksum = sorted(declared - set(checksums))
    if missing_from_checksum:
        errors.append("CHECKSUMS.SHA256: missing declared files " + ", ".join(missing_from_checksum) + ".")

    for rel_path, expected_hash in checksums.items():
        path = _safe_child(root, rel_path)
        if not path.is_file():
            errors.append(f"CHECKSUMS.SHA256: {rel_path} is listed but missing.")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_hash:
            errors.append(f"CHECKSUMS.SHA256: {rel_path} hash mismatch.")

    if strict:
        actual_files = {
            _rel_to(root, path)
            for path in root.rglob("*")
            if path.is_file() and path.name != "CHECKSUMS.SHA256"
        }
        missing = sorted(actual_files - set(checksums))
        extra = sorted(set(checksums) - actual_files)
        if missing:
            errors.append("--strict: CHECKSUMS.SHA256 missing pack files " + ", ".join(missing) + ".")
        if extra:
            errors.append("--strict: CHECKSUMS.SHA256 lists non-pack files " + ", ".join(extra) + ".")


def _validate_pack_safety(
    root: Path,
    manifest: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
    errors: list[str],
) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = _rel_to(root, path)
        if path.suffix.lower() in EXECUTABLE_EXTENSIONS:
            errors.append(f"{rel}: executable/archive payload extension is forbidden in Source Pack v0 examples.")
        if path.name == "CHECKSUMS.SHA256":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for phrase in FORBIDDEN_CLAIM_PHRASES:
            if phrase in lower:
                errors.append(f"{rel}: forbidden unsupported claim phrase {phrase!r}.")
        if "http://" in lower or "https://" in lower:
            errors.append(f"{rel}: live URL text is forbidden in the v0 example pack.")
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel}: private or absolute local path appears in pack text.")

    _validate_no_prohibited_keys(manifest, "SOURCE_PACK.json", errors)
    for record in records:
        label = str(record.get("evidence_id") or record.get("source_id") or record.get("representation_id") or "<record>")
        _validate_no_prohibited_keys(record, label, errors)


def _validate_docs(root: Path, errors: list[str]) -> None:
    rights_text = (root / "RIGHTS_AND_ACCESS.md").read_text(encoding="utf-8", errors="replace").lower()
    required = ("no executable", "does not claim rights clearance", "does not claim malware safety")
    for phrase in required:
        if phrase not in rights_text:
            errors.append(f"RIGHTS_AND_ACCESS.md: must state {phrase!r}.")


def _validate_jsonl_files(root: Path, rel_paths: Sequence[str], label: str, errors: list[str]) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for rel_path in rel_paths:
        path = _safe_child(root, rel_path)
        if not path.is_file():
            errors.append(f"{rel_path}: declared {label} JSONL file is missing.")
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel_path}:{line_number}: invalid JSONL: {exc.msg}.")
                continue
            if not isinstance(item, Mapping):
                errors.append(f"{rel_path}:{line_number}: JSONL record must be an object.")
                continue
            records.append(item)
    return records


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_display_path(path)}: missing JSON file.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_display_path(path)}: invalid JSON: {exc.msg}.")
        return None


def _load_jsonl_silent(path: Path) -> list[Any]:
    records: list[Any] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def _parse_checksums(path: Path, errors: list[str]) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split(None, 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            errors.append(f"CHECKSUMS.SHA256:{line_number}: expected '<sha256>  <relative-path>'.")
            continue
        rel_path = parts[1].strip()
        if rel_path.startswith("*"):
            rel_path = rel_path[1:]
        checksums[rel_path] = parts[0].lower()
    return checksums


def _validate_no_prohibited_keys(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in PROHIBITED_KEYS:
                errors.append(f"{label}: prohibited key {key!r} is not allowed in Source Pack v0.")
            _validate_no_prohibited_keys(child, label, errors)
    elif isinstance(value, list):
        for child in value:
            _validate_no_prohibited_keys(child, label, errors)


def _safe_child(root: Path, rel_path: str) -> Path:
    candidate = (root / rel_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return root / "__invalid_outside_pack__"
    return candidate


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _rel_to(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _display_path(path: Path) -> str:
    return _rel(path) if path.is_absolute() else str(path)


def _report(
    root: Path,
    manifest: Mapping[str, Any] | None,
    source_records: Sequence[Mapping[str, Any]],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_source_pack",
        "pack_root": _display_path(root),
        "pack_id": manifest.get("pack_id") if isinstance(manifest, Mapping) else None,
        "pack_version": manifest.get("pack_version") if isinstance(manifest, Mapping) else None,
        "pack_status": manifest.get("status") if isinstance(manifest, Mapping) else None,
        "source_record_count": len(source_records),
        "errors": errors,
        "warnings": warnings,
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Source Pack v0 validation",
        f"status: {report['status']}",
        f"pack_root: {report['pack_root']}",
    ]
    if report.get("pack_id"):
        lines.append(f"pack_id: {report['pack_id']}")
    lines.append(f"source_record_count: {report.get('source_record_count', 0)}")
    for error in report.get("errors", []):
        lines.append(f"ERROR: {error}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
