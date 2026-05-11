#!/usr/bin/env python3
"""Normalize one committed H8 manuals/docs/standards fixture offline."""

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

from runtime.connectors.h8_manuals_docs_standards.fixture_loader import load_h8_manuals_docs_fixture  # noqa: E402
from runtime.connectors.h8_manuals_docs_standards.normalizer_common import H8_SOURCE_IDS  # noqa: E402

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "control/inventory/sources",
    "harvest",
    "harvest_cache",
    "document_downloads",
    "standards_downloads",
    "pdf_downloads",
    "manual_downloads",
    "datasheet_downloads",
    "schematic_downloads",
    "service_manual_downloads",
    "ocr_cache",
    "iiif_cache",
    "media_downloads",
    "repair_manual_dumps",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)
ALLOWED_PREFIXES = (
    "examples/connectors/h8_manuals_docs_standards/normalized",
    "examples/connectors/h8_manuals_docs_standards/identity",
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
        raise ValueError(f"refusing output outside approved H8 fixture roots: {rel}")
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
    parser.add_argument("--source-id", required=True, choices=H8_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--document-output")
    parser.add_argument("--relation-output")
    parser.add_argument("--datasheet-output")
    parser.add_argument("--standard-output")
    parser.add_argument("--install-output")
    parser.add_argument("--repair-output")
    parser.add_argument("--access-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h8_manuals_docs_fixture(args.input)
        module = importlib.import_module(f"runtime.connectors.h8_manuals_docs_standards.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.document_output, normalized.get("technical_document_identity_candidate", {})),
            (args.relation_output, normalized.get("manual_artifact_relation_candidate", [])),
            (args.datasheet_output, normalized.get("datasheet_device_identity_candidate", {})),
            (args.standard_output, normalized.get("standards_specification_identity_candidate", {})),
            (args.install_output, normalized.get("install_requirement_claim_candidate", [])),
            (args.repair_output, normalized.get("repair_service_safety_candidate", [])),
            (args.access_output, normalized.get("access_rights_candidate", {})),
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
            "schema_version": "h8_manuals_docs_normalize_summary.v0",
            "status": "pass",
            "source_id": args.source_id,
            "normalized_record_id": normalized.get("normalized_record_id"),
            "technical_document_candidates": 1 if normalized.get("technical_document_identity_candidate") else 0,
            "manual_artifact_relation_candidates": len(normalized.get("manual_artifact_relation_candidate", []) or []),
            "datasheet_device_candidates": 1 if normalized.get("datasheet_device_identity_candidate") else 0,
            "standards_specification_candidates": 1 if normalized.get("standards_specification_identity_candidate") else 0,
            "install_requirement_candidates": len(normalized.get("install_requirement_claim_candidate", []) or []),
            "repair_service_safety_candidates": len(normalized.get("repair_service_safety_candidate", []) or []),
            "access_rights_candidates": 1 if normalized.get("access_rights_candidate") else 0,
            "network_calls_made": False,
            "query_fetch_download_extract_used": False,
            "restricted_source_access_used": False,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H8 manuals/docs/standards fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {args.source_id}", file=stdout)
            print(f"normalized_record_id: {summary['normalized_record_id']}", file=stdout)
            print("network_used: false", file=stdout)
            print("query_fetch_download_extract_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H8 manuals/docs/standards fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
