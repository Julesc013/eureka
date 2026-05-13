#!/usr/bin/env python3
"""Normalize one committed H14 Source OS rollup fixture offline."""

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

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import H14_SOURCE_IDS  # noqa: E402

SOURCE_MODULES = {
    "source_need_registry": "source_need_registry",
    "source_candidate_registry": "source_candidate_registry",
    "source_discovery_policy": "source_discovery_policy",
    "source_pack_manifest": "source_pack_manifest_source",
    "connector_pack_manifest": "connector_pack_manifest_source",
    "coverage_manifest": "coverage_manifest_source",
    "connector_scorecard": "connector_scorecard_source",
    "source_reliability_freshness": "source_reliability_freshness_source",
    "source_dispute_revocation": "source_dispute_revocation_source",
    "source_lineage_provenance": "source_lineage_provenance_source",
    "h14_policy_blocked": "h14_policy_blocked",
}
ALLOWED_PREFIXES = (
    "examples/connectors/h14_source_discovery/normalized",
    "examples/connectors/h14_source_discovery/identity",
    "examples/connectors/h14_source_discovery/replay_results",
    "control/audits/h14-bundle-02-source-discovery-fixture-runtime-v0/generated",
)
FORBIDDEN_PREFIXES = (
    "site/dist", "data/public_index", "runtime", "contracts", "control/inventory/sources", "control/inventory/connectors",
    "control/inventory/source_packs", "source_registry_mutation", "connector_registry_mutation", "pack_import_staging",
    "pack_export_staging", "source_discovery_runtime", "external_source_fetch", "source_cache", "evidence_ledger",
    "review_queue", "master_index", ".aide.local", ".local/eureka", ".cache/eureka", "local_sources", "private_sources", "cas_store",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H14_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--source-need-output")
    parser.add_argument("--source-candidate-output")
    parser.add_argument("--discovery-output")
    parser.add_argument("--source-pack-output")
    parser.add_argument("--connector-pack-output")
    parser.add_argument("--coverage-output")
    parser.add_argument("--scorecard-output")
    parser.add_argument("--reliability-output")
    parser.add_argument("--dispute-output")
    parser.add_argument("--lineage-output")
    parser.add_argument("--pack-boundary-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h14_source_discovery_fixture(args.input)
        module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h14_source_discovery.{SOURCE_MODULES[args.source_id]}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.source_need_output, normalized["source_need_candidate"]),
            (args.source_candidate_output, normalized["source_candidate_candidate"]),
            (args.discovery_output, normalized["source_discovery_candidate"]),
            (args.source_pack_output, normalized["source_pack_manifest_candidate"]),
            (args.connector_pack_output, normalized["connector_pack_manifest_candidate"]),
            (args.coverage_output, normalized["coverage_manifest_candidate"]),
            (args.scorecard_output, normalized["connector_scorecard_candidate"]),
            (args.reliability_output, normalized["source_reliability_freshness_candidate"]),
            (args.dispute_output, normalized["source_dispute_revocation_candidate"]),
            (args.lineage_output, normalized["source_lineage_provenance_candidate"]),
            (args.pack_boundary_output, normalized["pack_import_export_boundary_candidate"]),
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
            print("H14 source discovery fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {normalized['source_id']}", file=stdout)
            print("fixture_only: true", file=stdout)
            print("source_discovery_runtime: false", file=stdout)
            print("pack_export_import: false", file=stdout)
            print("registry_mutation: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 source discovery fixture normalization", file=stdout)
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
            raise ValueError("output path must be under H14 fixture examples/audit roots or an explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    for forbidden in FORBIDDEN_PREFIXES:
        if rel_lower == forbidden or rel_lower.startswith(forbidden.rstrip("/") + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    if any(rel_lower == prefix or rel_lower.startswith(prefix.rstrip("/") + "/") for prefix in allowed_prefixes):
        return resolved
    raise ValueError("repo output path must be under H14 fixture examples or audit generated roots")


if __name__ == "__main__":
    raise SystemExit(main())
