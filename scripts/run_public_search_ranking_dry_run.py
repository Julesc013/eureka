from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.engine.ranking.dry_run import approved_root_from_text, run_public_search_ranking_dry_run  # noqa: E402
from runtime.engine.ranking.errors import RankingDryRunError  # noqa: E402
from runtime.engine.ranking.policy import (  # noqa: E402
    APPROVED_EXAMPLE_ROOTS,
    validate_no_forbidden_cli_args,
    validate_output_path,
)
from runtime.engine.ranking.report import report_to_json, summarize_report  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    try:
        validate_no_forbidden_cli_args(raw_args)
    except RankingDryRunError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser(description="Run local public-search ranking dry-run over approved examples.")
    parser.add_argument("--all-examples", action="store_true", help="Run all approved ranking dry-run examples.")
    parser.add_argument("--example-root", action="append", default=[], help="Approved repo-local example root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero on invalid result sets or fallback.")
    parser.add_argument("--output", help="Optional approved output path for JSON report.")
    args = parser.parse_args(raw_args)

    roots: list[Path] = []
    try:
        if args.example_root:
            roots = [approved_root_from_text(path_text) for path_text in args.example_root]
        elif args.all_examples:
            roots = [root for root in APPROVED_EXAMPLE_ROOTS if root.exists()]
        else:
            roots = [root for root in APPROVED_EXAMPLE_ROOTS if root.exists()]
        report = run_public_search_ranking_dry_run(roots, strict=args.strict)
    except RankingDryRunError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_text = report_to_json(report) if args.json else summarize_report(report)
    if args.output:
        try:
            output_path = validate_output_path(args.output)
        except RankingDryRunError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_to_json(report), encoding="utf-8")

    sys.stdout.write(output_text)
    if args.strict and report.result_sets_invalid:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

