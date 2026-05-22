"""Shared helpers for P70 contract validators.

This module is stdlib-only and local. It performs no network calls,
telemetry, persistence, source calls, cache writes, ledger writes, or index
mutation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence


SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("windows_absolute_path_slash", re.compile(r"\b[A-Za-z]:/+(?:users|documents|temp|windows|projects|private|local)/+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d{1,3}[\s.-]+)?(?:\(?\d{2,4}\)?[\s.-]+){2,}\d{2,4}\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key)\b|\b(?:secret|credential)\s*[:=]", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\s*[:=]", re.IGNORECASE)),
)


def load_json_object(path: Path, errors: list[str], label: str | None = None) -> dict[str, Any]:
    label = label or str(path)
    if not path.is_file():
        errors.append(f"{label} missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} does not parse as JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{label} must contain a JSON object.")
        return {}
    return payload


def require_fields(payload: Mapping[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    missing = required - set(payload)
    if missing:
        errors.append(f"{prefix} missing required fields: {', '.join(sorted(missing))}")


def require_false(section: Mapping[str, Any], fields: Iterable[str], errors: list[str], prefix: str) -> None:
    for field in fields:
        if section.get(field) is not False:
            errors.append(f"{prefix}.{field} must be false.")


def require_true(section: Mapping[str, Any], fields: Iterable[str], errors: list[str], prefix: str) -> None:
    for field in fields:
        if section.get(field) is not True:
            errors.append(f"{prefix}.{field} must be true.")


def check_allowed(value: Any, allowed: set[str], errors: list[str], field: str) -> None:
    if value not in allowed:
        errors.append(f"{field} has invalid value {value!r}; allowed: {', '.join(sorted(allowed))}")


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from iter_strings(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for nested in value:
            yield from iter_strings(nested)


def check_sensitive(payload: Any, errors: list[str], prefix: str) -> None:
    text = "\n".join(iter_strings(payload))
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append(f"{prefix} contains prohibited sensitive pattern: {label}")


def validate_checksums(root: Path, target_filename: str, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    target_path = root / target_filename
    if not checksum_path.is_file():
        errors.append(f"{root}/CHECKSUMS.SHA256 missing.")
        return
    if not target_path.is_file():
        errors.append(f"{target_path} missing.")
        return
    expected = None
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and parts[1] == target_filename:
            expected = parts[0]
            break
    if expected is None:
        errors.append(f"{checksum_path} does not reference {target_filename}.")
        return
    observed = hashlib.sha256(target_path.read_bytes()).hexdigest()
    if observed != expected:
        errors.append(f"{target_filename} checksum mismatch in {root}.")


def print_report(report: Mapping[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2))
        return
    print(f"status: {report['status']}")
    for key in ("record_count", "example_count", "contract_file", "report_id"):
        if key in report:
            print(f"{key}: {report[key]}")
    if report.get("errors"):
        print("errors:")
        for error in report["errors"]:
            print(f"  - {error}")
    if report.get("warnings"):
        print("warnings:")
        for warning in report["warnings"]:
            print(f"  - {warning}")
