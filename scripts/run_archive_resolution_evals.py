from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.engine.evals import (  # noqa: E402
    build_default_archive_resolution_eval_runner,
    format_archive_resolution_eval_summary,
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run Eureka's bounded Archive Resolution Eval Runner v0 over the current "
            "archive-resolution eval packet."
        ),
    )
    parser.add_argument(
        "--task",
        dest="task_id",
        help="Optional archive-resolution eval task id to run by itself.",
    )
    parser.add_argument(
        "--index-path",
        help="Optional explicit bootstrap Local Index v0 SQLite path to build and query.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the stable JSON report.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the JSON report to stdout instead of the plain text summary.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    runner = build_default_archive_resolution_eval_runner()
    suite = runner.run_suite(task_id=args.task_id, index_path=args.index_path)
    report = suite.to_dict()

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True))
        output.write("\n")
    else:
        output.write(format_archive_resolution_eval_summary(suite))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
