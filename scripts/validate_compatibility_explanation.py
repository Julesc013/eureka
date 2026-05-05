#!/usr/bin/env python3
"""Validate Compatibility Explanation v0 examples."""

import argparse
import json
from pathlib import Path
import sys
from typing import Mapping, Sequence, TextIO


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
TOP_LEVEL_REQUIRED = {'compatibility_explanation_kind', 'result_suppressed', 'action_safety_explanations', 'no_installability_without_evidence_guarantees', 'explanation_applied_to_live_search', 'target_profile_summary', 'conflict_explanations', 'public_user_text', 'factor_explanations', 'explanation_generated_by_runtime', 'created_by_tool', 'schema_version', 'compatibility_ranking_applied_to_live_search', 'installability_claimed', 'no_runtime_guarantees', 'compatibility_status_explanations', 'limitations', 'explanation_scope', 'notes', 'hidden_suppression_performed', 'compatibility_explanation_id', 'status', 'item_explanations', 'unknown_gap_explanations'}
HARD_FALSE_FIELDS = {"explanation_generated_by_runtime", "explanation_applied_to_live_search", "compatibility_ranking_applied_to_live_search", "installability_claimed", "result_suppressed", "hidden_suppression_performed"}


def validate_explanation(path: Path, *, example_root: Path | None = None) -> list[str]:
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
    if page.get("compatibility_explanation_kind") != "compatibility_explanation":
        errors.append("compatibility_explanation_kind must be compatibility_explanation")
    check_false_map(page, HARD_FALSE_FIELDS, "explanation", errors)
    for key in ("target_profile_summary", "public_user_text"):
        if not page.get(key):
            errors.append(f"{key} must be present")
    for key in ("item_explanations", "factor_explanations", "compatibility_status_explanations", "unknown_gap_explanations", "action_safety_explanations"):
        if not isinstance(page.get(key), list) or not page.get(key):
            errors.append(f"{key} must be a non-empty list")
    public_text = str(page.get("public_user_text", "")).lower()
    for phrase in ("not installability proof", "compatibility truth"):
        if phrase not in public_text:
            errors.append(f"public_user_text must include cautious phrase: {phrase}")
    check_public_safe(page, errors)
    if example_root is not None:
        check_checksums(example_root, errors)
    return errors


def example_paths() -> list[tuple[Path, Path]]:
    return [(p, p.parent) for p in sorted(EXAMPLES_ROOT.glob("*/COMPATIBILITY_EXPLANATION.json"))]


def validate_all_examples() -> tuple[list[Path], list[str]]:
    paths = example_paths()
    errors: list[str] = []
    for path, root in paths:
        errors.extend(validate_explanation(path, example_root=root))
    return [path for path, _ in paths], errors


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--explanation")
    parser.add_argument("--explanation-root")
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    if args.all_examples:
        paths, errors = validate_all_examples()
    elif args.explanation:
        path = Path(args.explanation)
        root = Path(args.explanation_root) if args.explanation_root else None
        paths, errors = [path], validate_explanation(path, example_root=root)
    else:
        paths, errors = [], ["choose --explanation or --all-examples"]
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
