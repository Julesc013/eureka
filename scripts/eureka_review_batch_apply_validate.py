#!/usr/bin/env python3
"""Validate the review-batch apply plan before temp local apply."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_apply import (  # noqa: E402
    build_review_batch_apply_plan,
    evaluate_review_batch_apply_eligibility,
    load_review_batch_apply_inputs,
    validate_review_batch_apply_plan,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Use committed review/candidate examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    inputs = load_review_batch_apply_inputs()
    eligibility = evaluate_review_batch_apply_eligibility(inputs["candidates"], inputs["review_packets"], [])
    eligible_items = _eligible_items(inputs["candidates"], eligibility)
    plan = build_review_batch_apply_plan(eligible_items, inputs["known_needs"], inputs["absence_summaries"])
    result = validate_review_batch_apply_plan(plan)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def _eligible_items(candidates: Sequence[dict], eligibility: Sequence[dict]) -> list[dict]:
    by_id = {candidate["candidate_id"]: dict(candidate) for candidate in candidates}
    items: list[dict] = []
    for row in eligibility:
        if row.get("eligible"):
            item = dict(by_id[row["candidate_id"]])
            item.update(row)
            item["review_batch_ref"] = item.get("review_batch_packet_ref", "")
            items.append(item)
    return items


if __name__ == "__main__":
    raise SystemExit(main())
