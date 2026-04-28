from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT_ROOT = REPO_ROOT / "snapshots" / "examples" / "static_snapshot_v0"
SNAPSHOT_CONTRACT = REPO_ROOT / "control" / "inventory" / "publication" / "snapshot_contract.json"

REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "snapshot_contract_id",
    "status",
    "stability",
    "snapshot_format_version",
    "production_signed_release",
    "real_signing_keys_present",
    "contains_real_binaries",
    "contains_live_backend",
    "contains_live_probes",
    "contains_external_observations",
    "required_files",
    "optional_files",
    "checksum_policy",
    "signature_policy",
    "public_data_included",
    "file_tree_policy",
    "client_profiles",
    "prohibited_contents",
    "created_by_slice",
    "notes",
}
REQUIRED_FILES = {
    "README_FIRST.txt",
    "index.html",
    "index.txt",
    "SNAPSHOT_MANIFEST.json",
    "BUILD_MANIFEST.json",
    "SOURCE_SUMMARY.json",
    "EVAL_SUMMARY.json",
    "ROUTE_SUMMARY.json",
    "PAGE_REGISTRY.json",
    "CHECKSUMS.SHA256",
    "SIGNATURES.README.txt",
    "data/README.txt",
}
JSON_FILES = {
    "SNAPSHOT_MANIFEST.json",
    "BUILD_MANIFEST.json",
    "SOURCE_SUMMARY.json",
    "EVAL_SUMMARY.json",
    "ROUTE_SUMMARY.json",
    "PAGE_REGISTRY.json",
}
FORBIDDEN_SUFFIXES = {
    ".exe",
    ".dll",
    ".msi",
    ".dmg",
    ".pkg",
    ".zip",
    ".7z",
    ".tar",
    ".gz",
    ".pem",
    ".key",
    ".pfx",
    ".p12",
    ".env",
    ".sqlite",
    ".sqlite3",
    ".db",
}
LOCAL_ABSOLUTE_PATH = re.compile(r"([A-Za-z]:\\|/Users/|/home/|/tmp/|/var/)")
POSITIVE_CLAIMS = (
    re.compile(r"\bproduction signed release\b", re.IGNORECASE),
    re.compile(r"\breal private keys? (are|is) (included|present|stored)\b", re.IGNORECASE),
    re.compile(r"\bexecutable downloads? (are|is) (included|available|provided)\b", re.IGNORECASE),
    re.compile(r"\blive backend (is )?(available|enabled|included)\b", re.IGNORECASE),
    re.compile(r"\blive probes? (are )?(available|enabled|included)\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka static snapshot seed example.")
    parser.add_argument(
        "--snapshot-root",
        default=str(DEFAULT_SNAPSHOT_ROOT),
        help="Snapshot directory to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_static_snapshot(Path(args.snapshot_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_static_snapshot(snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    snapshot_root = snapshot_root.resolve()

    contract = _load_json(SNAPSHOT_CONTRACT, errors)
    _validate_contract(contract, errors)
    _validate_required_files(snapshot_root, errors)
    payloads = _validate_json_files(snapshot_root, errors)
    checksum_entries = _validate_checksums(snapshot_root, errors)
    _validate_signature_readme(snapshot_root, errors)
    _validate_file_safety(snapshot_root, errors)
    _validate_payload_flags(payloads, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "static_snapshot_validator_v0",
        "snapshot_root": _display_path(snapshot_root),
        "snapshot_contract": _display_path(SNAPSHOT_CONTRACT),
        "required_files": sorted(REQUIRED_FILES),
        "json_files": sorted(JSON_FILES),
        "checksum_entries": sorted(checksum_entries),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("snapshot_contract.json: must be a JSON object.")
        return
    missing = sorted(REQUIRED_CONTRACT_FIELDS - set(payload))
    if missing:
        errors.append(f"snapshot_contract.json: missing fields {missing}.")
    if payload.get("schema_version") != "0.1.0":
        errors.append("snapshot_contract.json: schema_version must be 0.1.0.")
    if payload.get("snapshot_format_version") != "0.1.0":
        errors.append("snapshot_contract.json: snapshot_format_version must be 0.1.0.")
    for flag in (
        "production_signed_release",
        "real_signing_keys_present",
        "contains_real_binaries",
        "contains_live_backend",
        "contains_live_probes",
        "contains_external_observations",
    ):
        if payload.get(flag) is not False:
            errors.append(f"snapshot_contract.json: {flag} must be false.")
    required = set(payload.get("required_files", []))
    missing_required = sorted((REQUIRED_FILES - {"data/README.txt"}) - required)
    if missing_required:
        errors.append(f"snapshot_contract.json: required_files missing {missing_required}.")
    signature = payload.get("signature_policy")
    if not isinstance(signature, Mapping):
        errors.append("snapshot_contract.json: signature_policy must be an object.")
    else:
        if signature.get("status") != "placeholder_only":
            errors.append("snapshot_contract.json: signature_policy.status must be placeholder_only.")
        if signature.get("real_private_keys_allowed_in_repo") is not False:
            errors.append("snapshot_contract.json: real private keys must be disallowed.")


def _validate_required_files(snapshot_root: Path, errors: list[str]) -> None:
    if not snapshot_root.is_dir():
        errors.append(f"{_display_path(snapshot_root)}: snapshot root is missing.")
        return
    for relative in sorted(REQUIRED_FILES):
        if not (snapshot_root / relative).is_file():
            errors.append(f"{_display_path(snapshot_root / relative)}: required snapshot file is missing.")


def _validate_json_files(snapshot_root: Path, errors: list[str]) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for relative in sorted(JSON_FILES):
        path = snapshot_root / relative
        payload = _load_json(path, errors)
        payloads[relative] = payload
    return payloads


def _validate_checksums(snapshot_root: Path, errors: list[str]) -> set[str]:
    path = snapshot_root / "CHECKSUMS.SHA256"
    entries: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"{_display_path(path)}: checksum file is missing.")
        return set()
    for number, line in enumerate(lines, start=1):
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"{_display_path(path)}:{number}: invalid SHA256SUMS line.")
            continue
        digest, relative = parts
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"{_display_path(path)}:{number}: digest must be lowercase sha256 hex.")
            continue
        if relative == "CHECKSUMS.SHA256":
            errors.append(f"{_display_path(path)}:{number}: CHECKSUMS.SHA256 must not checksum itself.")
            continue
        target = snapshot_root / relative
        if not target.is_file():
            errors.append(f"{_display_path(path)}:{number}: target file missing: {relative}.")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"{_display_path(path)}:{number}: checksum mismatch for {relative}.")
        entries[relative] = digest
    expected = {
        str(item.relative_to(snapshot_root)).replace("\\", "/")
        for item in snapshot_root.rglob("*")
        if item.is_file() and item.name != "CHECKSUMS.SHA256"
    }
    missing = sorted(expected - set(entries))
    extra = sorted(set(entries) - expected)
    if missing:
        errors.append(f"CHECKSUMS.SHA256: missing entries {missing}.")
    if extra:
        errors.append(f"CHECKSUMS.SHA256: unexpected entries {extra}.")
    return set(entries)


def _validate_signature_readme(snapshot_root: Path, errors: list[str]) -> None:
    path = snapshot_root / "SIGNATURES.README.txt"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{_display_path(path)}: signature README missing.")
        return
    lowered = text.casefold()
    for phrase in (
        "no production signing is performed",
        "no private keys are stored",
        "not full authenticity proof",
    ):
        if phrase not in lowered:
            errors.append(f"{_display_path(path)}: missing signature limitation phrase {phrase!r}.")


def _validate_file_safety(snapshot_root: Path, errors: list[str]) -> None:
    if not snapshot_root.exists():
        return
    for path in sorted(snapshot_root.rglob("*")):
        if not path.is_file():
            continue
        relative = _display_path(path)
        suffixes = {suffix.lower() for suffix in path.suffixes}
        if suffixes & FORBIDDEN_SUFFIXES:
            errors.append(f"{relative}: forbidden snapshot file type.")
        if path.stat().st_size > 512 * 1024:
            errors.append(f"{relative}: seed snapshot file is unexpectedly large.")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{relative}: seed snapshot files must be text/JSON only.")
            continue
        if LOCAL_ABSOLUTE_PATH.search(text):
            errors.append(f"{relative}: local absolute path appears in snapshot file.")
        for pattern in POSITIVE_CLAIMS:
            for match in pattern.finditer(text):
                context = text[max(0, match.start() - 80) : match.end() + 80].casefold()
                if any(token in context for token in ("not a", "no ", "none", "false", "placeholder")):
                    continue
                errors.append(f"{relative}: prohibited positive claim {match.group(0)!r}.")


def _validate_payload_flags(payloads: Mapping[str, Any], errors: list[str]) -> None:
    for name, payload in payloads.items():
        if not isinstance(payload, Mapping):
            continue
        for flag in (
            "production_signed_release",
            "real_signing_keys_present",
            "contains_real_binaries",
            "contains_live_backend",
            "contains_live_probes",
            "contains_external_observations",
        ):
            if flag in payload and payload[flag] is not False:
                errors.append(f"{name}: {flag} must be false when present.")
    manifest = payloads.get("SNAPSHOT_MANIFEST.json")
    if isinstance(manifest, Mapping):
        if manifest.get("snapshot_format_version") != "0.1.0":
            errors.append("SNAPSHOT_MANIFEST.json: snapshot_format_version must be 0.1.0.")
        if manifest.get("checksum_file") != "CHECKSUMS.SHA256":
            errors.append("SNAPSHOT_MANIFEST.json: checksum_file must be CHECKSUMS.SHA256.")
        if manifest.get("signature_placeholder") != "SIGNATURES.README.txt":
            errors.append("SNAPSHOT_MANIFEST.json: signature placeholder mismatch.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_display_path(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_display_path(path)}: invalid JSON: {exc}.")
    return {}


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static snapshot validation",
        f"status: {report['status']}",
        f"snapshot_root: {report['snapshot_root']}",
        f"checksum_entries: {len(report['checksum_entries'])}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
