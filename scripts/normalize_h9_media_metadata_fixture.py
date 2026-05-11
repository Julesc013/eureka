#!/usr/bin/env python3
"""Normalize one committed H9 media metadata fixture offline."""

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

from runtime.connectors.h9_media_metadata.fixture_loader import load_h9_media_metadata_fixture  # noqa: E402
from runtime.connectors.h9_media_metadata.normalizer_common import H9_SOURCE_IDS  # noqa: E402

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "control/inventory/sources",
    "media_downloads",
    "media_uploads",
    "fingerprint_cache",
    "fingerprint_uploads",
    "image_cache",
    "video_cache",
    "audio_cache",
    "map_downloads",
    "score_downloads",
    "ocr_cache",
    "restricted_sources",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)
ALLOWED_PREFIXES = (
    "examples/connectors/h9_media_metadata/normalized",
    "examples/connectors/h9_media_metadata/identity",
)


def safe_output_path(path_text: str | Path, allowed_prefixes: tuple[str, ...] = ALLOWED_PREFIXES) -> Path:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_root = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_root).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        for prefix in allowed_prefixes:
            prefix_lower = prefix.casefold().rstrip("/")
            if rel_lower == prefix_lower or rel_lower.startswith(prefix_lower + "/"):
                return resolved
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved H9 fixture roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H9_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--media-output")
    parser.add_argument("--music-output")
    parser.add_argument("--visual-output")
    parser.add_argument("--relation-output")
    parser.add_argument("--fingerprint-output")
    parser.add_argument("--rights-output")
    parser.add_argument("--safety-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h9_media_metadata_fixture(args.input)
        module = importlib.import_module(f"runtime.connectors.h9_media_metadata.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.media_output, normalized.get("media_object_identity_candidate", {})),
            (args.music_output, normalized.get("music_work_recording_release_candidate", {})),
            (args.visual_output, normalized.get("image_video_map_identity_candidate", {})),
            (args.relation_output, normalized.get("media_creator_collection_relation_candidate", [])),
            (args.fingerprint_output, normalized.get("media_fingerprint_candidate", {})),
            (args.rights_output, normalized.get("media_rights_license_candidate", {})),
            (args.safety_output, normalized.get("media_safety_privacy_candidate", {})),
            (args.source_cache_output, normalized.get("source_cache_candidate_preview", {})),
            (args.evidence_preview_output, normalized.get("evidence_candidate_preview", {})),
        ]
        if not args.check:
            for output_path, payload in outputs:
                if output_path:
                    path = safe_output_path(output_path)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h9_media_metadata_normalize_summary.v0",
            "status": "pass",
            "source_id": args.source_id,
            "normalized_record_id": normalized.get("normalized_record_id"),
            "media_object_candidates": 1 if normalized.get("media_object_identity_candidate") else 0,
            "music_recording_release_candidates": 1 if normalized.get("music_work_recording_release_candidate") else 0,
            "image_video_map_candidates": 1 if normalized.get("image_video_map_identity_candidate") else 0,
            "creator_collection_relation_candidates": len(normalized.get("media_creator_collection_relation_candidate", []) or []),
            "fingerprint_candidates": 1 if normalized.get("media_fingerprint_candidate") else 0,
            "rights_license_candidates": 1 if normalized.get("media_rights_license_candidate") else 0,
            "safety_privacy_candidates": 1 if normalized.get("media_safety_privacy_candidate") else 0,
            "network_calls_made": False,
            "download_upload_fingerprint_used": False,
            "restricted_source_access_used": False,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H9 media metadata fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {args.source_id}", file=stdout)
            print(f"normalized_record_id: {summary['normalized_record_id']}", file=stdout)
            print("network_used: false", file=stdout)
            print("download_upload_fingerprint_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H9 media metadata fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
