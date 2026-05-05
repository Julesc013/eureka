#!/usr/bin/env python3
"""Validate Compatibility Target Profile v0 examples."""

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FINGERPRINT_RE = re.compile(r"(machine[-_ ]?fingerprint|hardware[-_ ]?fingerprint)", re.IGNORECASE)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def iter_values(value: Any):
    if isinstance(value, Mapping):
        for item in value.values():
            yield from iter_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_values(item)
    else:
        yield value


def check_public_safe(value: Any, errors: list[str], *, allow_fingerprint_words: bool = False) -> None:
    for item in iter_values(value):
        if not isinstance(item, str):
            continue
        if PRIVATE_PATH_RE.search(item):
            errors.append(f"private path-like value found: {item}")
        if SECRET_RE.search(item):
            errors.append(f"secret-like value found: {item}")
        if IP_RE.search(item):
            errors.append(f"IP address-like value found: {item}")
        if ACCOUNT_RE.search(item):
            errors.append(f"account identifier-like value found: {item}")
        if not allow_fingerprint_words and FINGERPRINT_RE.search(item):
            errors.append(f"local machine fingerprint-like value found: {item}")


def check_false_map(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not False:
            errors.append(f"{prefix}.{field} must be false")


def check_true(data: Mapping[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    if data.get(field) is not True:
        errors.append(f"{prefix}.{field} must be true")


def check_checksums(root: Path, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.exists():
        errors.append(f"missing checksum file: {checksum_path}")
        return
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, name = line.split(None, 1)
        target = root / name.strip()
        if not target.exists():
            errors.append(f"checksum target missing: {target}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"checksum mismatch for {target}")


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "compatibility_aware_ranking"
TOP_LEVEL_REQUIRED = {'hardware_peripheral_driver_requirements', 'private_path_included', 'target_environment', 'compatibility_target_profile_id', 'architecture_requirements', 'privacy', 'runtime_profile_store_implemented', 'emulator_vm_reconstruction_requirements', 'created_by_tool', 'schema_version', 'no_runtime_guarantees', 'limitations', 'notes', 'user_profile_tracking_enabled', 'compatibility_target_profile_kind', 'persistent_profile_store_implemented', 'runtime_dependency_requirements', 'telemetry_exported', 'credentials_included', 'local_machine_fingerprint_included', 'profile_identity', 'status', 'action_preferences', 'platform_requirements'}
HARD_FALSE_FIELDS = {
    "runtime_profile_store_implemented",
    "persistent_profile_store_implemented",
    "user_profile_tracking_enabled",
    "telemetry_exported",
    "private_path_included",
    "credentials_included",
    "local_machine_fingerprint_included",
}
STATUSES = {"draft_example", "dry_run_validated", "synthetic_example", "public_safe_example", "local_private_future", "runtime_future", "rejected_by_policy"}
ENV_KINDS = {"physical_machine", "virtual_machine", "emulator", "compatibility_layer", "operating_system_only", "package_runtime", "browser_runtime", "unknown"}
GOALS = {"run_natively", "run_in_vm", "run_in_emulator", "inspect_metadata", "find_compatible_version", "compare_compatibility", "preserve_or_reconstruct", "unknown"}


def validate_profile(path: Path, *, example_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    try:
        page = load_json(path)
    except Exception as exc:
        return [f"{display_path(path, REPO_ROOT)} failed to parse: {exc}"]
    if not isinstance(page, Mapping):
        return [f"{display_path(path, REPO_ROOT)} must be an object"]
    missing = sorted(TOP_LEVEL_REQUIRED - set(page))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    if page.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0")
    if page.get("compatibility_target_profile_kind") != "compatibility_target_profile":
        errors.append("compatibility_target_profile_kind must be compatibility_target_profile")
    if page.get("status") not in STATUSES:
        errors.append("status is not allowed")
    check_false_map(page, HARD_FALSE_FIELDS, "profile", errors)
    env = page.get("target_environment")
    if not isinstance(env, Mapping):
        errors.append("target_environment must be an object")
    else:
        if env.get("target_environment_kind") not in ENV_KINDS:
            errors.append("target_environment.target_environment_kind is not allowed")
        if env.get("compatibility_goal") not in GOALS:
            errors.append("target_environment.compatibility_goal is not allowed")
        for key in ("operating_systems", "os_versions", "architectures", "runtime_requirements", "hardware_requirements", "driver_requirements"):
            if key not in env:
                errors.append(f"target_environment.{key} is required")
    privacy = page.get("privacy")
    if not isinstance(privacy, Mapping):
        errors.append("privacy must be an object")
    else:
        for key in ("contains_private_path", "contains_secret", "contains_private_url", "contains_user_identifier", "contains_ip_address", "contains_raw_private_query", "contains_local_machine_fingerprint"):
            if privacy.get(key) is not False:
                errors.append(f"privacy.{key} must be false")
    check_public_safe(page, errors, allow_fingerprint_words=True)
    if example_root is not None:
        check_checksums(example_root, errors)
    return errors


def example_paths() -> list[tuple[Path, Path]]:
    return [(p, p.parent) for p in sorted(EXAMPLES_ROOT.glob("*/COMPATIBILITY_TARGET_PROFILE.json"))]


def validate_all_examples() -> tuple[list[Path], list[str]]:
    paths = example_paths()
    errors: list[str] = []
    for path, root in paths:
        errors.extend(validate_profile(path, example_root=root))
    return [path for path, _ in paths], errors


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile")
    parser.add_argument("--profile-root")
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    errors: list[str] = []
    paths: list[Path] = []
    if args.all_examples:
        paths, errors = validate_all_examples()
    elif args.profile:
        path = Path(args.profile)
        root = Path(args.profile_root) if args.profile_root else None
        paths = [path]
        errors = validate_profile(path, example_root=root)
    else:
        errors = ["choose --profile or --all-examples"]
    status = "invalid" if errors else "valid"
    if args.json:
        print(json.dumps({"status": status, "example_count": len(paths), "validated_paths": [display_path(p, REPO_ROOT) for p in paths], "errors": errors}, indent=2), file=stdout)
    else:
        print(f"status: {status}", file=stdout)
        print(f"example_count: {len(paths)}", file=stdout)
        for error in errors:
            print(f"ERROR: {error}", file=stdout)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
