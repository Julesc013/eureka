#!/usr/bin/env python3
"""Normalize one committed H10 games/emulation fixture offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h10_games_emulation.normalizer_common import H10_SOURCE_IDS  # noqa: E402

ALLOWED_PREFIXES = (
    "examples/connectors/h10_games_emulation/normalized",
    "examples/connectors/h10_games_emulation/identity",
    "control/audits/h10-bundle-02-games-emulation-fixture-runtime-v0/generated",
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
    "chd",
    "bios",
    "firmware",
    "game_binaries",
    "emulators",
    "installers",
    "patches",
    "game_installs",
    "launchers",
    "hash_submissions",
    "storefront_accounts",
    "restricted_sources",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H10_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--game-output")
    parser.add_argument("--release-output")
    parser.add_argument("--compatibility-output")
    parser.add_argument("--hashset-output")
    parser.add_argument("--media-output")
    parser.add_argument("--relation-output")
    parser.add_argument("--action-output")
    parser.add_argument("--rights-safety-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h10_games_emulation_fixture(args.input)
        module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h10_games_emulation.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.game_output, normalized["game_software_identity_candidate"]),
            (args.release_output, normalized["platform_release_edition_candidate"]),
            (args.compatibility_output, normalized["emulator_compatibility_candidate"]),
            (args.hashset_output, normalized["preservation_hashset_candidate"]),
            (args.media_output, normalized["rom_disc_media_identity_candidate"]),
            (args.relation_output, normalized["game_relation_candidate"]),
            (args.action_output, normalized["emulator_action_candidate"]),
            (args.rights_safety_output, normalized["games_rights_safety_candidate"]),
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
            print("H10 games/emulation fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {normalized['source_id']}", file=stdout)
            print("fixture_only: true", file=stdout)
            print("network_used: false", file=stdout)
            print("download_upload_execute_acquire: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H10 games/emulation fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def safe_output_path(output: str | Path, allowed_prefixes: Sequence[str] = ALLOWED_PREFIXES) -> Path:
    path = Path(output)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved
    for forbidden in FORBIDDEN_PREFIXES:
        if rel == forbidden or rel.startswith(forbidden.rstrip("/") + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    if rel.startswith("control/audits/") and "/generated/" in rel:
        return resolved
    if rel.startswith("examples/connectors/h10_games_emulation/"):
        return resolved
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
