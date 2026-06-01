#!/usr/bin/env python3
"""Summarize seed-batch examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.seed_batches import (  # noqa: E402
    run_seed_batch_frontier_media,
    run_seed_batch_legacy_software,
    run_seed_batch_manuals_scans,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated fixture examples.")
    parser.add_argument(
        "--domain",
        choices=("frontier_media", "legacy_software", "manuals_scans"),
        default="frontier_media",
        help="Seed-batch example domain.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    example_result = REPO_ROOT / "examples" / "seed_batches" / args.domain / "seed_batch_result.json"
    if example_result.exists():
        result = _load_example_result(example_result)
    elif args.domain == "manuals_scans":
        result = run_seed_batch_manuals_scans(fixture=True)
    elif args.domain == "legacy_software":
        result = run_seed_batch_legacy_software(fixture=True)
    else:
        result = run_seed_batch_frontier_media(fixture=True)
    task = {
        "frontier_media": "SEED-BATCH-FRONTIER-MEDIA-00",
        "legacy_software": "SEED-BATCH-LEGACY-SOFTWARE-00",
        "manuals_scans": "SEED-BATCH-MANUALS-SCANS-00",
    }[args.domain]
    report = {
        "schema_version": "seed_batch_report.v0",
        "task": task,
        "status": "pass" if result.get("fixture_seed_batch_passed") else "partial",
        "batch_id": result.get("batch_id"),
        "domain": args.domain,
        "query_count": result.get("query_count"),
        "candidate_count": result.get("candidate_count"),
        "review_batch_refs": result.get("review_batch_refs", []),
        "snapshot_refresh_handoff_refs": result.get("snapshot_refresh_handoff_refs", []),
        "public_alpha_reassess_refs": result.get("public_alpha_reassess_refs", []),
        "operator_live_metadata_run_performed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "download_performed": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "extraction_executed": False,
        "install_execution_enabled": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "cracks_keygens_serials_supported": False,
        "malware_clean_claims_created": False,
        "rights_clearance_claim_created": False,
        "scan_completeness_claim_created": False,
        "ocr_quality_claim_created": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0


def _load_example_result(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
