#!/usr/bin/env python3
"""Build a dry-run candidate ingest packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.candidate_store import (  # noqa: E402
    archive_org_candidate_to_record,
    build_candidate_index_write_plan,
    sample_archive_org_candidate,
)
from runtime.search.query_plan import plan_query_to_source_actions  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-archive-org-example", action="store_true", help="Use the bundled IA metadata example.")
    parser.add_argument("--query", required=True, help="Query that produced the source candidate.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Emit a write plan without applying it.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)

    if not args.from_archive_org_example:
        parser.error("--from-archive-org-example is required for this offline CLI")

    query_plan = plan_query_to_source_actions(args.query)
    candidate = archive_org_candidate_to_record(sample_archive_org_candidate(args.query), query_plan)
    write_plan = build_candidate_index_write_plan(candidate, "temp_store")
    payload = {
        "schema_version": "candidate_ingest_cli_result.v0",
        "dry_run": True,
        "query": args.query,
        "candidate_record": candidate,
        "write_plan": write_plan,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
