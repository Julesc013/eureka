#!/usr/bin/env python3
"""Normalize one committed H5 vendor/update fixture offline."""

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

from runtime.connectors.h5_vendor_update_driver.fixture_loader import load_h5_vendor_update_fixture  # noqa: E402
from runtime.connectors.h5_vendor_update_driver.normalizer_common import H5_SOURCE_IDS  # noqa: E402


from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "control/inventory/sources",
    "vendor_downloads",
    "firmware_staging",
    "package_cache",
    "data/package_cache",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)

def safe_output_path(path_text: str | Path, allowed_prefixes: tuple[str, ...]) -> Path:
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
        raise ValueError(f"refusing output outside approved H5 fixture roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


ALLOWED_PREFIXES = (
    "examples/connectors/h5_vendor_update_driver/normalized",
    "examples/connectors/h5_vendor_update_driver/identity",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H5_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--vendor-identity-output")
    parser.add_argument("--compatibility-output")
    parser.add_argument("--firmware-output")
    parser.add_argument("--runtime-output")
    parser.add_argument("--payload-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h5_vendor_update_fixture(args.input)
        module = importlib.import_module(f"runtime.connectors.h5_vendor_update_driver.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.vendor_identity_output, normalized.get("vendor_identity_candidate", {})),
            (args.compatibility_output, normalized.get("driver_device_compatibility_candidate_preview", [])),
            (args.firmware_output, normalized.get("firmware_update_candidate_preview", [])),
            (args.runtime_output, normalized.get("runtime_redistributable_candidate_preview", [])),
            (args.payload_output, normalized.get("payload_metadata_candidate_preview", [])),
            (args.source_cache_output, normalized.get("source_cache_candidate_preview", {})),
            (args.evidence_preview_output, normalized.get("evidence_candidate_preview", {})),
        ]
        if not args.check:
            for output_path, payload in outputs:
                if output_path:
                    path = safe_output_path(output_path, ALLOWED_PREFIXES)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h5_vendor_update_normalize_summary.v0",
            "status": "pass",
            "source_id": args.source_id,
            "normalized_record_id": normalized.get("normalized_record_id"),
            "vendor_identity_candidates": 1,
            "compatibility_candidates": len(normalized.get("driver_device_compatibility_candidate_preview", [])),
            "firmware_candidates": len(normalized.get("firmware_update_candidate_preview", [])),
            "runtime_candidates": len(normalized.get("runtime_redistributable_candidate_preview", [])),
            "payload_candidates": len(normalized.get("payload_metadata_candidate_preview", [])),
            "network_calls_made": False,
            "downloads_made": False,
            "firmware_flashes_made": False,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H5 vendor/update fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {args.source_id}", file=stdout)
            print(f"normalized_record_id: {summary['normalized_record_id']}", file=stdout)
            print("network_used: false", file=stdout)
            print("downloads_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H5 vendor/update fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
