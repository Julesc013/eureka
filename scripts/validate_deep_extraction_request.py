
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = ROOT / "examples" / "extraction"

TIERS = {
    "tier_0_outer_metadata",
    "tier_1_container_member_listing",
    "tier_2_manifest_extraction",
    "tier_3_selective_text_summary",
    "tier_4_recursive_deep_extraction",
    "tier_5_on_demand_deepening",
    "OCR_hook_future",
    "transcription_hook_future",
    "unknown",
}
TARGET_KINDS = {
    "public_index_document",
    "object_page_record",
    "source_cache_record_future",
    "evidence_pack_record",
    "source_pack_record",
    "pack_member",
    "static_fixture",
    "synthetic_example",
    "unknown",
}
TARGET_STATUSES = {"synthetic_example", "fixture", "reviewed_future", "candidate", "unknown"}
CONTAINER_KINDS = {
    "zip_archive",
    "tar_archive",
    "gzip_archive",
    "seven_zip_archive",
    "ISO_image",
    "disk_image",
    "installer",
    "package_archive",
    "wheel",
    "sdist",
    "npm_tarball",
    "WARC",
    "WACZ",
    "PDF",
    "scanned_volume",
    "source_bundle",
    "repository_snapshot",
    "unknown",
}
CONTAINER_STATUSES = {"synthetic_example", "metadata_only", "fixture_summary", "future_runtime", "unknown"}
MEMBER_KINDS = {
    "file",
    "directory",
    "manifest",
    "metadata_record",
    "capture_record",
    "OCR_layer",
    "text_segment",
    "image",
    "executable",
    "installer_member",
    "nested_archive",
    "source_file",
    "unknown",
}
MEMBER_STATUSES = {"synthetic_example", "listed_only", "metadata_only", "future_runtime", "rejected_by_policy"}
MANIFEST_KINDS = {
    "package_manifest",
    "installer_manifest",
    "disc_manifest",
    "WARC_index",
    "WACZ_manifest",
    "METS",
    "ALTO",
    "IIIF_manifest",
    "checksums_manifest",
    "SBOM",
    "SPDX",
    "PURL_metadata",
    "unknown",
}
MANIFEST_STATUSES = {"synthetic_example", "metadata_only", "future_runtime", "missing", "unknown"}
TEXT_SOURCE_KINDS = {
    "manifest_text",
    "metadata_text",
    "OCR_text_future",
    "PDF_text_future",
    "README_text_future",
    "source_comment_text_future",
    "unknown",
}
TEXT_STATUSES = {"synthetic_example", "summary_only", "future_runtime", "not_available"}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def require(data: dict[str, Any], fields: list[str], path: Path) -> None:
    for field in fields:
        if field not in data:
            raise ValidationError(f"{path}: missing required field {field}")


def expect_false(data: dict[str, Any], fields: list[str], path: Path) -> None:
    for field in fields:
        if data.get(field) is not False:
            raise ValidationError(f"{path}: {field} must be false")


def expect_enum(value: str, allowed: set[str], label: str, path: Path) -> None:
    if value not in allowed:
        raise ValidationError(f"{path}: {label} has unsupported value {value!r}")


def public_safe_path(value: str) -> bool:
    if not value:
        return True
    lower = value.lower()
    if "://" in value or lower.startswith(("file:", "data:", "javascript:")):
        return False
    if value.startswith(("/", "\\")) or "\\" in value:
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    parts = value.replace("\\", "/").split("/")
    if any(part in {"..", "~"} for part in parts):
        return False
    if any(part.lower() in {"users", "home", "private", "secrets", ".ssh", ".env"} for part in parts):
        return False
    return True


def walk_strings(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)
    elif isinstance(value, str):
        yield value


SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b\d{10,}\b"),
]


def validate_no_private_strings(data: Any, path: Path) -> None:
    for value in walk_strings(data):
        if "://" in value or value.lower().startswith(("file:", "data:", "javascript:")):
            raise ValidationError(f"{path}: arbitrary URL-like value is not allowed: {value!r}")
        if not public_safe_path(value) and ("/" in value or "\\" in value or re.match(r"^[A-Za-z]:", value)):
            raise ValidationError(f"{path}: private or unsafe path value is not allowed: {value!r}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(value):
                raise ValidationError(f"{path}: secret, contact, IP, or account-like value is not allowed")


def validate_checksums(root: Path) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.exists():
        raise ValidationError(f"{root}: missing CHECKSUMS.SHA256")
    expected = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, name = line.split(None, 1)
        except ValueError as exc:
            raise ValidationError(f"{checksum_path}: malformed checksum line") from exc
        expected[name.strip()] = digest.strip()
    if not expected:
        raise ValidationError(f"{checksum_path}: no checksum entries")
    for name, digest in expected.items():
        candidate = root / name
        if not candidate.exists():
            raise ValidationError(f"{checksum_path}: listed file missing: {name}")
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != digest:
            raise ValidationError(f"{checksum_path}: checksum mismatch for {name}")


def example_roots() -> list[Path]:
    if not EXAMPLES_ROOT.exists():
        return []
    return sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())


def emit(ok: bool, checked: list[str], errors: list[str], json_mode: bool) -> int:
    if json_mode:
        print(json.dumps({"ok": ok, "checked": checked, "error_count": len(errors), "errors": errors}, indent=2, sort_keys=True))
    elif ok:
        print(f"validation passed: {len(checked)} item(s)")
    else:
        for error in errors:
            print(error, file=sys.stderr)
    return 0 if ok else 1


REQUEST_HARD_FALSE = [
    "runtime_extraction_implemented",
    "extraction_executed",
    "files_opened",
    "archive_unpacked",
    "payload_executed",
    "installer_executed",
    "package_manager_invoked",
    "emulator_vm_launched",
    "OCR_performed",
    "transcription_performed",
    "live_source_called",
    "external_calls_performed",
    "URL_fetched",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "telemetry_exported",
]

REQUIRED = [
    "schema_version",
    "extraction_request_id",
    "extraction_request_kind",
    "status",
    "created_by_tool",
    "request_scope",
    "target_ref",
    "extraction_policy_ref",
    "requested_tiers",
    "container_hints",
    "safety_requirements",
    "privacy",
    "rights_risk",
    "expected_outputs",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
] + REQUEST_HARD_FALSE


def validate_request(path: Path, check_checksum: bool = False) -> None:
    data = load_json(path)
    require(data, REQUIRED, path)
    if data["extraction_request_kind"] != "deep_extraction_request":
        raise ValidationError(f"{path}: extraction_request_kind must be deep_extraction_request")
    expect_enum(data["status"], {"draft_example", "dry_run_validated", "synthetic_example", "public_safe_example", "review_required", "rejected_by_policy", "runtime_future"}, "status", path)
    expect_false(data, REQUEST_HARD_FALSE, path)
    if not data["requested_tiers"]:
        raise ValidationError(f"{path}: requested_tiers must not be empty")
    for tier in data["requested_tiers"]:
        expect_enum(tier, TIERS, "requested_tiers", path)
    target = data["target_ref"]
    require(target, ["target_kind", "target_label", "target_identifier", "target_status", "target_payload_available", "limitations"], path)
    expect_enum(target["target_kind"], TARGET_KINDS, "target_ref.target_kind", path)
    expect_enum(target["target_status"], TARGET_STATUSES, "target_ref.target_status", path)
    if target.get("target_payload_available") is not False:
        raise ValidationError(f"{path}: target_payload_available must be false")
    if target.get("target_path_public_safe") and not public_safe_path(target["target_path_public_safe"]):
        raise ValidationError(f"{path}: target_path_public_safe must be public-safe")
    if not data["container_hints"]:
        raise ValidationError(f"{path}: container_hints must not be empty")
    for container in data["container_hints"]:
        require(container, ["container_kind", "container_label", "container_status", "payload_included", "executable_risk_present", "nested_container_present", "limitations"], path)
        expect_enum(container["container_kind"], CONTAINER_KINDS, "container_kind", path)
        expect_enum(container["container_status"], CONTAINER_STATUSES, "container_status", path)
        if container.get("payload_included") is not False:
            raise ValidationError(f"{path}: container payload_included must be false")
    for field in ("safety_requirements", "privacy", "rights_risk"):
        if not isinstance(data[field], dict) or not data[field]:
            raise ValidationError(f"{path}: {field} must be a non-empty object")
    validate_no_private_strings(data, path)
    if check_checksum:
        validate_checksums(path.parent)


def paths_from_args(args: argparse.Namespace) -> list[tuple[Path, bool]]:
    if args.request:
        return [(Path(args.request), False)]
    if args.request_root:
        return [(Path(args.request_root) / "DEEP_EXTRACTION_REQUEST.json", True)]
    roots = example_roots()
    return [(root / "DEEP_EXTRACTION_REQUEST.json", True) for root in roots]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka Deep Extraction Request v0 examples.")
    parser.add_argument("--request")
    parser.add_argument("--request-root")
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    checked: list[str] = []
    errors: list[str] = []
    for path, check_checksum in paths_from_args(args):
        try:
            validate_request(path, check_checksum)
            checked.append(str(path.relative_to(ROOT) if path.is_absolute() and path.is_relative_to(ROOT) else path))
        except Exception as exc:
            errors.append(str(exc))
    if not checked and not errors:
        errors.append("no deep extraction request examples found")
    return emit(not errors, checked, errors, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
