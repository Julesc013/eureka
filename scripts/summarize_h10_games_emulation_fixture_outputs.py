#!/usr/bin/env python3
"""Summarize H10 games/emulation fixture outputs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h10_games_emulation.normalizer_common import H10_SOURCE_IDS  # noqa: E402
from scripts.normalize_h10_games_emulation_fixture import safe_output_path  # noqa: E402

ALLOWED_PREFIXES = (
    "examples/connectors/h10_games_emulation/normalized",
    "examples/connectors/h10_games_emulation/replay_results",
    "examples/connectors/h10_games_emulation/identity",
    "control/audits/h10-bundle-02-games-emulation-fixture-runtime-v0/generated",
)
KNOWN_SOURCE_IDS = set(H10_SOURCE_IDS)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    inputs = args.input or ["examples/connectors/h10_games_emulation"]
    try:
        summary = summarize_inputs(inputs)
        if not args.check:
            for output in (args.output, args.summary_output):
                if output:
                    path = safe_output_path(output, ALLOWED_PREFIXES)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if str(output).endswith(".md"):
                        path.write_text(render_summary_markdown(summary), encoding="utf-8")
                    else:
                        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H10 games/emulation fixture output summary", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_records: {summary['normalized_record_count']}", file=stdout)
            print(f"replay_results: {summary['fixture_replay_result_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H10 games/emulation fixture output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def summarize_inputs(inputs: Sequence[str | Path]) -> dict[str, Any]:
    files: list[Path] = []
    for item in inputs:
        path = Path(item)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
    source_ids: set[str] = set()
    counts = {
        "normalized_record_count": 0,
        "fixture_replay_result_count": 0,
        "game_software_identity_candidate_count": 0,
        "platform_release_edition_candidate_count": 0,
        "emulator_compatibility_candidate_count": 0,
        "preservation_hashset_candidate_count": 0,
        "rom_disc_media_identity_candidate_count": 0,
        "game_relation_candidate_count": 0,
        "emulator_action_candidate_count": 0,
        "rights_safety_candidate_count": 0,
        "source_cache_candidate_preview_count": 0,
        "evidence_candidate_preview_count": 0,
    }
    blockers: list[str] = []
    warnings: list[str] = []
    for file_path in files:
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        walk_payload(payload, source_ids, counts, blockers, warnings)
    return {
        "schema_version": "h10_games_emulation_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(source_ids),
        "sources": sorted(source_ids),
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "network_calls_made": False,
        "download_upload_execute_acquire_used": False,
        "restricted_source_access_used": False,
        **counts,
    }


def walk_payload(payload: Any, source_ids: set[str], counts: dict[str, int], blockers: list[str], warnings: list[str]) -> None:
    if isinstance(payload, dict):
        source_id = payload.get("source_id")
        if isinstance(source_id, str) and source_id in KNOWN_SOURCE_IDS:
            source_ids.add(source_id)
        schema = payload.get("schema_version")
        if schema == "h10_games_emulation_normalized_record.v0":
            counts["normalized_record_count"] += 1
        elif schema == "h10_games_emulation_fixture_replay_result.v0":
            counts["fixture_replay_result_count"] += 1
            if payload.get("replay_status") == "blocked_by_policy_fixture":
                blockers.append(str(payload.get("source_id")))
        elif schema == "h10_game_software_identity_candidate.v0":
            counts["game_software_identity_candidate_count"] += 1
        elif schema == "h10_platform_release_edition_candidate.v0":
            counts["platform_release_edition_candidate_count"] += 1
        elif schema == "h10_emulator_compatibility_candidate.v0":
            counts["emulator_compatibility_candidate_count"] += 1
        elif schema == "h10_preservation_hashset_candidate.v0":
            counts["preservation_hashset_candidate_count"] += 1
        elif schema == "h10_rom_disc_media_identity_candidate.v0":
            counts["rom_disc_media_identity_candidate_count"] += 1
        elif schema == "h10_game_relation_candidate.v0":
            counts["game_relation_candidate_count"] += 1
        elif schema == "h10_emulator_action_candidate.v0":
            counts["emulator_action_candidate_count"] += 1
        elif schema == "h10_games_rights_safety_candidate.v0":
            counts["rights_safety_candidate_count"] += 1
        elif schema == "h10_games_emulation_source_cache_candidate_preview.v0":
            counts["source_cache_candidate_preview_count"] += 1
        elif schema == "h10_games_emulation_evidence_candidate_preview.v0":
            counts["evidence_candidate_preview_count"] += 1
        for value in payload.values():
            walk_payload(value, source_ids, counts, blockers, warnings)
    elif isinstance(payload, list):
        for item in payload:
            walk_payload(item, source_ids, counts, blockers, warnings)


def render_summary_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# H10 Games/Emulation Fixture Output Summary",
            "",
            f"- status: {summary['status']}",
            f"- source_count: {summary['source_count']}",
            f"- normalized_record_count: {summary['normalized_record_count']}",
            f"- fixture_replay_result_count: {summary['fixture_replay_result_count']}",
            f"- network_calls_made: {str(summary['network_calls_made']).lower()}",
            f"- download_upload_execute_acquire_used: {str(summary['download_upload_execute_acquire_used']).lower()}",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
