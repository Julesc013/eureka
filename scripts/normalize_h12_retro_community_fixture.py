#!/usr/bin/env python3
"""Normalize one committed H12 retro/community fixture offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h12_retro_community.normalizer_common import H12_SOURCE_IDS  # noqa: E402

ALLOWED_PREFIXES = (
    "examples/connectors/h12_retro_community/normalized",
    "examples/connectors/h12_retro_community/identity",
    "examples/connectors/h12_retro_community/replay_results",
    "control/audits/h12-bundle-02-retro-community-fixture-runtime-v0/generated",
)
FORBIDDEN_PREFIXES = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "roms",
    "isos",
    "disc_images",
    "emulators",
    "bios",
    "firmware",
    "vintage_software_downloads",
    "installers",
    "patches",
    "cracks",
    "keys",
    "serials",
    "gated_source_accounts",
    "forum_sessions",
    "archive_extractions",
    "download_actions",
    "install_actions",
    "execution_actions",
    "acquisition_actions",
    "restricted_sources",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H12_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--software-output")
    parser.add_argument("--platform-output")
    parser.add_argument("--archive-output")
    parser.add_argument("--compatibility-output")
    parser.add_argument("--community-output")
    parser.add_argument("--hash-output")
    parser.add_argument("--corroboration-output")
    parser.add_argument("--gated-boundary-output")
    parser.add_argument("--rights-safety-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h12_retro_community_fixture(args.input)
        module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h12_retro_community.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.software_output, normalized["retro_software_identity_candidate"]),
            (args.platform_output, normalized["platform_version_edition_candidate"]),
            (args.archive_output, normalized["archive_item_member_candidate"]),
            (args.compatibility_output, normalized["compatibility_install_note_candidate"]),
            (args.community_output, normalized["community_review_comment_candidate"]),
            (args.hash_output, normalized["hash_checksum_candidate"]),
            (args.corroboration_output, normalized["ia_wayback_corroboration_candidate"]),
            (args.gated_boundary_output, normalized["gated_source_boundary_candidate"]),
            (args.rights_safety_output, normalized["retro_rights_safety_candidate"]),
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
            print("H12 retro/community fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {normalized['source_id']}", file=stdout)
            print("fixture_only: true", file=stdout)
            print("network_used: false", file=stdout)
            print("download_extract_execute_acquire: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H12 retro/community fixture normalization", file=stdout)
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
            raise ValueError("output path must be under H12 fixture examples/audit roots or an explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    for forbidden in FORBIDDEN_PREFIXES:
        if rel_lower == forbidden or rel_lower.startswith(forbidden.rstrip("/") + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    if any(rel_lower == prefix or rel_lower.startswith(prefix.rstrip("/") + "/") for prefix in allowed_prefixes):
        return resolved
    raise ValueError("repo output path must be under H12 fixture examples or audit generated roots")


if __name__ == "__main__":
    raise SystemExit(main())
