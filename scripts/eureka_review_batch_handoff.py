#!/usr/bin/env python3
"""Build review-batch local-apply and snapshot handoff previews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.review.batch import run_review_batch_from_examples  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-candidate-examples", action="store_true", help="Use bundled local examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_candidate_examples:
        parser.error("--from-candidate-examples is required for this offline CLI")
    payload = run_review_batch_from_examples(
        decision="accept_local_reviewed_preview",
        operator_context={"projection_profile": "operator_workbench", "dry_run": True},
    )
    handoff = payload.get("decision_preview", {})
    print(
        json.dumps(
            {
                "schema_version": "review_batch_handoff_cli_result.v0",
                "local_apply_handoff": handoff.get("local_apply_handoff"),
                "snapshot_refresh_handoff": handoff.get("snapshot_refresh_handoff"),
                "accepted_truth": False,
                "reviewed_index_mutated": False,
                "master_index_mutated": False,
                "public_mutation_enabled": False,
            },
            indent=2,
            sort_keys=True,
        ),
        file=stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
