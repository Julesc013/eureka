#!/usr/bin/env python3
"""Render the PUBLIC-SEARCH-UX-MVP-00 no-JS public search examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_search import build_public_search_ux_mvp_bundle  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-view-model-examples",
        action="store_true",
        help="Render from committed public search view-model projection examples.",
    )
    parser.add_argument("--write-examples", action="store_true", help="Write HTML/text examples plus inventory/audit evidence.")
    parser.add_argument("--query", default="D-Theater New York", help="Example query for the results page.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    if not args.from_view_model_examples:
        parser.error("--from-view-model-examples is required")

    result = build_public_search_ux_mvp_bundle(query=args.query, write_examples=args.write_examples)
    payload = {
        "schema_version": result["schema_version"],
        "task": result["task"],
        "status": result["status"],
        "result_card_count": len(result["result_cards"]),
        "routes": result["routes"],
        "examples_written_paths": result["examples_written_paths"],
        "no_js_search_form_passed": result["no_js_search_form_passed"],
        "candidate_verified_distinction_passed": result["candidate_verified_distinction_passed"],
        "limited_reviewed_record_distinction_passed": result["limited_reviewed_record_distinction_passed"],
        "public_projection_read_only": result["public_projection_read_only"],
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
