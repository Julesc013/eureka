#!/usr/bin/env python3
"""Normalize one committed H13 local/private fixture offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h13_local_private.normalizer_common import H13_SOURCE_IDS  # noqa: E402

ALLOWED_PREFIXES = (
    "examples/connectors/h13_local_private/normalized",
    "examples/connectors/h13_local_private/identity",
    "examples/connectors/h13_local_private/replay_results",
    "control/audits/h13-bundle-02-local-private-fixture-runtime-v0/generated",
)
FORBIDDEN_PREFIXES = (
    "site/dist", "site/dist/data/public_index", "runtime", "contracts", "control/inventory/publication", "control/inventory/sources",
    "local_sources", "cas", "cas_roots", "private_sources", "credential_directories", "credentials", "user_url_fetches", "accounts",
    "import_export_staging", "pack_exports", "pack_imports", "archive_extractions", "execution_actions", "acquisition_actions",
    "source_cache", "evidence_ledger", "review_queue", "master_index", ".aide.local", ".local/eureka", ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H13_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--local-source-output")
    parser.add_argument("--private-boundary-output")
    parser.add_argument("--url-boundary-output")
    parser.add_argument("--authenticated-boundary-output")
    parser.add_argument("--restricted-manifest-output")
    parser.add_argument("--cas-boundary-output")
    parser.add_argument("--pack-boundary-output")
    parser.add_argument("--privacy-output")
    parser.add_argument("--rights-safety-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h13_local_private_fixture(args.input)
        module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h13_local_private.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.local_source_output, normalized["local_source_identity_candidate"]),
            (args.private_boundary_output, normalized["private_source_boundary_candidate"]),
            (args.url_boundary_output, normalized["user_supplied_url_boundary_candidate"]),
            (args.authenticated_boundary_output, normalized["authenticated_source_boundary_candidate"]),
            (args.restricted_manifest_output, normalized["restricted_source_manifest_candidate"]),
            (args.cas_boundary_output, normalized["local_cas_import_boundary_candidate"]),
            (args.pack_boundary_output, normalized["pack_export_import_boundary_candidate"]),
            (args.privacy_output, normalized["privacy_redaction_candidate"]),
            (args.rights_safety_output, normalized["local_private_rights_safety_candidate"]),
            (args.source_cache_output, normalized["source_cache_candidate_preview"]),
            (args.evidence_preview_output, normalized["evidence_candidate_preview"]),
        ]
        if not args.check:
            for output, payload in outputs:
                if output:
                    path = safe_output_path(output, ALLOWED_PREFIXES)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(normalized, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {normalized['source_id']}", file=stdout)
            print("fixture_only: true", file=stdout)
            print("local_private_access: false", file=stdout)
            print("cas_import_pack_export_publication: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H13 local/private fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def safe_output_path(output: str | Path, allowed_prefixes: Sequence[str] = ALLOWED_PREFIXES) -> Path:
    path = Path(output)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise ValueError("output path must be under H13 fixture examples/audit roots or an explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    for forbidden in FORBIDDEN_PREFIXES:
        if rel_lower == forbidden or rel_lower.startswith(forbidden.rstrip("/") + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    if any(rel_lower == prefix or rel_lower.startswith(prefix.rstrip("/") + "/") for prefix in allowed_prefixes):
        return resolved
    raise ValueError("repo output path must be under H13 fixture examples or audit generated roots")


if __name__ == "__main__":
    raise SystemExit(main())
