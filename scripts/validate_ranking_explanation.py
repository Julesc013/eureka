#!/usr/bin/env python3
"""Validate Ranking Explanation v0 examples."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "evidence_weighted_ranking"

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "ranking_explanation_id",
    "ranking_explanation_kind",
    "status",
    "created_by_tool",
    "explanation_scope",
    "item_explanations",
    "factor_explanations",
    "uncertainty_explanations",
    "conflict_explanations",
    "gap_explanations",
    "tie_break_explanations",
    "public_user_text",
    "limitations",
    "no_hidden_suppression_guarantees",
    "no_runtime_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "explanation_generated_by_runtime",
    "explanation_applied_to_live_search",
    "result_suppressed",
    "hidden_suppression_performed",
    "ranking_applied_to_live_search",
}
STATUSES = {"draft_example", "dry_run_validated", "synthetic_example", "public_safe_example", "runtime_future"}
PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FORBIDDEN_KEYS = {
    "ranking_path",
    "scoring_path",
    "source_cache_path",
    "evidence_ledger_path",
    "candidate_path",
    "promotion_path",
    "index_path",
    "store_root",
    "local_path",
    "database_path",
    "source_root",
    "private_local_path",
    "download_url",
    "install_url",
    "execute_url",
    "raw_source_payload",
    "source_credentials",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_strings(value: Any, key_path: str = ""):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield from iter_strings(item, f"{key_path}.{key}" if key_path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{key_path}[{index}]")
    elif isinstance(value, str):
        yield key_path, value


def iter_keys(value: Any, key_path: str = ""):
    if isinstance(value, Mapping):
        for key, item in value.items():
            path = f"{key_path}.{key}" if key_path else str(key)
            yield path, str(key)
            yield from iter_keys(item, path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_keys(item, f"{key_path}[{index}]")


def checksum_errors(example_root: Path) -> list[str]:
    checksum_path = example_root / "CHECKSUMS.SHA256"
    errors: list[str] = []
    if not checksum_path.exists():
        return [f"{example_root}: missing CHECKSUMS.SHA256"]
    for line_number, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            errors.append(f"{checksum_path}:{line_number}: invalid checksum line")
            continue
        expected, rel = parts
        file_path = example_root / rel.strip()
        if not file_path.exists():
            errors.append(f"{checksum_path}:{line_number}: missing checksummed file {rel}")
            continue
        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"{checksum_path}:{line_number}: checksum mismatch for {rel}")
    return errors


def check_false(errors: list[str], path: str, value: Any) -> None:
    if value is not False:
        errors.append(f"{path} must be false")


def validate_sensitive_content(page: Mapping[str, Any], errors: list[str]) -> None:
    for key_path, key in iter_keys(page):
        if key in FORBIDDEN_KEYS:
            errors.append(f"{key_path}: forbidden key {key!r}")
    for key_path, text in iter_strings(page):
        if PRIVATE_PATH_RE.search(text):
            errors.append(f"{key_path}: contains private absolute path or file URL")
        if SECRET_RE.search(text):
            errors.append(f"{key_path}: contains credential-like text")
        if IP_RE.search(text):
            errors.append(f"{key_path}: contains IP address")
        if ACCOUNT_RE.search(text):
            errors.append(f"{key_path}: contains account/user identifier")


def validate_explanation(page: Mapping[str, Any], *, source: str = "<memory>") -> list[str]:
    errors: list[str] = []
    missing = sorted(TOP_LEVEL_REQUIRED - page.keys())
    if missing:
        errors.append(f"{source}: missing required fields: {', '.join(missing)}")
    if page.get("schema_version") != "0.1.0":
        errors.append(f"{source}: schema_version must be 0.1.0")
    if page.get("ranking_explanation_kind") != "ranking_explanation":
        errors.append(f"{source}: ranking_explanation_kind must be ranking_explanation")
    if page.get("status") not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}, got {page.get('status')!r}")
    for key in HARD_FALSE_FIELDS:
        check_false(errors, key, page.get(key))

    for key in ("item_explanations", "factor_explanations"):
        value = page.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"{key} must be a non-empty list")
    for key in ("uncertainty_explanations", "conflict_explanations", "gap_explanations", "tie_break_explanations"):
        if not isinstance(page.get(key), list):
            errors.append(f"{key} must be a list")

    text = str(page.get("public_user_text", "")).lower()
    if not text.strip():
        errors.append("public_user_text must be present")
    if "not truth" not in text or "not applied to live search" not in text:
        errors.append("public_user_text must be cautious about truth and live-search application")

    guarantees = page.get("no_hidden_suppression_guarantees", {})
    if isinstance(guarantees, Mapping):
        check_false(errors, "no_hidden_suppression_guarantees.result_suppressed", guarantees.get("result_suppressed"))
        check_false(
            errors,
            "no_hidden_suppression_guarantees.hidden_suppression_performed",
            guarantees.get("hidden_suppression_performed"),
        )
        if guarantees.get("public_reason_required") is not True:
            errors.append("no_hidden_suppression_guarantees.public_reason_required must be true")

    validate_sensitive_content(page, errors)
    return errors


def validate_path(path: Path, *, check_checksums: bool = True) -> list[str]:
    try:
        page = load_json(path)
    except Exception as exc:
        return [f"{path}: failed to parse JSON: {exc}"]
    if not isinstance(page, Mapping):
        return [f"{path}: explanation must be an object"]
    errors = validate_explanation(page, source=str(path))
    if check_checksums and path.name == "RANKING_EXPLANATION.json" and path.parent.parent == EXAMPLES_ROOT:
        errors.extend(checksum_errors(path.parent))
    return errors


def example_paths() -> list[Path]:
    return sorted(EXAMPLES_ROOT.glob("*/RANKING_EXPLANATION.json"))


def validate_all_examples() -> tuple[list[Path], list[str]]:
    paths = example_paths()
    errors: list[str] = []
    if not paths:
        errors.append("no ranking explanation examples found")
    for path in paths:
        errors.extend(validate_path(path))
    return paths, errors


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def emit(status: str, paths: Sequence[Path], errors: Sequence[str], *, as_json: bool, stream: TextIO) -> None:
    if as_json:
        print(
            json.dumps(
                {
                    "status": status,
                    "example_count": len(paths),
                    "validated_paths": [display_path(path) for path in paths],
                    "errors": list(errors),
                },
                indent=2,
            ),
            file=stream,
        )
    else:
        print(f"status: {status}", file=stream)
        print(f"example_count: {len(paths)}", file=stream)
        for error in errors:
            print(f"error: {error}", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--explanation", type=Path)
    parser.add_argument("--explanation-root", type=Path)
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    paths: list[Path] = []
    errors: list[str] = []
    if args.all_examples:
        paths, errors = validate_all_examples()
    elif args.explanation:
        paths = [args.explanation]
        errors = validate_path(args.explanation, check_checksums=False)
    elif args.explanation_root:
        path = args.explanation_root / "RANKING_EXPLANATION.json"
        paths = [path]
        errors = validate_path(path, check_checksums=False)
    else:
        errors.append("provide --explanation, --explanation-root, or --all-examples")

    status = "valid" if not errors else "invalid"
    emit(status, paths, errors, as_json=args.json, stream=sys.stdout)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
