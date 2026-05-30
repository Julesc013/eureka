#!/usr/bin/env python3
"""Print a deterministic source-action query plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.search.query_plan import plan_query_to_source_actions


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="*", help="Query text to plan.")
    parser.add_argument("--query", dest="query_option", help="Query text to plan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default output shape.")
    args = parser.parse_args(argv)

    query = args.query_option or " ".join(args.query)
    if not query.strip():
        parser.error("query is required")
    plan = plan_query_to_source_actions(query)
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True), file=stdout)
    else:
        print(json.dumps(plan, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
