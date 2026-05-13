#!/usr/bin/env python3
"""Normalize one committed H4 code/source/release fixture offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h4_code_source_release.fixture_loader import load_h4_code_source_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import H4_SOURCE_IDS  # noqa: E402

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "control/inventory/sources",
    "repository_clones",
    "repository_mirrors",
    "package_cache",
    "data/package_cache",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H4_SOURCE_IDS)
    parser.add_argument("--input", required=True, help="Committed fixture JSON file.")
    parser.add_argument("--output", help="Optional normalized record output path.")
    parser.add_argument("--source-identity-output", help="Optional source identity candidate output path.")
    parser.add_argument("--release-identity-output", help="Optional release identity candidate output path.")
    parser.add_argument("--relation-output", help="Optional source-to-binary relation candidate output path.")
    parser.add_argument("--asset-output", help="Optional release asset candidate output path.")
    parser.add_argument("--source-cache-output", help="Optional source-cache candidate preview output path.")
    parser.add_argument("--evidence-preview-output", help="Optional evidence candidate preview output path.")
    parser.add_argument("--check", action="store_true", help="Validate and normalize without writing files.")
    parser.add_argument("--json", action="store_true", help="Print normalized JSON.")
    args = parser.parse_args(argv)
    try:
        fixture = load_h4_code_source_fixture(_repo_path(args.input))
        normalizer = _normalizer(args.source_id)
        normalized = normalizer(fixture)
        outputs = {
            "output": normalized,
            "source_identity_output": normalized.get("source_identity_candidate"),
            "release_identity_output": normalized.get("release_identity_candidate"),
            "relation_output": normalized.get("source_to_binary_relation_candidate_preview", []),
            "asset_output": normalized.get("release_asset_candidate_preview", []),
            "source_cache_output": normalized.get("source_cache_candidate_preview"),
            "evidence_preview_output": normalized.get("evidence_candidate_preview"),
        }
        if not args.check:
            for attr, payload in outputs.items():
                target = getattr(args, attr)
                if target:
                    _write_json(target, payload)
        if args.json:
            print(json.dumps(normalized, indent=2, sort_keys=True), file=stdout)
        else:
            print("H4 code/source fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {normalized['source_id']}", file=stdout)
            print(f"normalized_record_id: {normalized['normalized_record_id']}", file=stdout)
            print("network_used: false", file=stdout)
            print("repository_clone_used: false", file=stdout)
            print("source_archive_download_used: false", file=stdout)
            print("release_asset_download_used: false", file=stdout)
            print("git_command_invoked: false", file=stdout)
            print("build_tool_invoked: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H4 code/source fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def _normalizer(source_id: str):
    module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h4_code_source_release.{source_id}")
    return module.normalize


def _repo_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def _write_json(path_text: str, payload: Any) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_root = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_root).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/connectors/h4_code_source_release/"):
            return resolved
        raise ValueError(f"refusing output outside approved H4 fixture roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())
