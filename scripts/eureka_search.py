#!/usr/bin/env python3
"""Run the local Eureka search MVP from the command line."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.search_mvp import (
    HARD_QUERY_SMOKE_SET,
    LocalSearchOptions,
    LocalSearchService,
    render_search_html,
    render_search_json,
    render_search_text,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="*", help="Search query text.")
    parser.add_argument("--all", action="store_true", help="Run the fixed hard-query smoke set.")
    parser.add_argument("--format", choices=("text", "json", "html_basic"), default="text")
    parser.add_argument("--metadata-fallback", choices=("none", "ia_fixture"), default="none")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--show-evidence", action="store_true")
    parser.add_argument("--show-debug", action="store_true")
    args = parser.parse_args(argv)

    query = " ".join(args.query).strip()
    if not args.all and not query:
        parser.error("provide a query or use --all")

    options = LocalSearchOptions(
        metadata_fallback=args.metadata_fallback,
        limit=args.limit,
        show_evidence=args.show_evidence,
        show_debug=args.show_debug,
    )
    service = LocalSearchService()
    response = service.search_many(HARD_QUERY_SMOKE_SET, options) if args.all else service.search(query, options)
    if args.format == "json":
        print(render_search_json(response), end="", file=stdout)
    elif args.format == "html_basic":
        print(render_search_html(response), end="", file=stdout)
    else:
        print(render_search_text(response), end="", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
