#!/usr/bin/env python3
"""Run the P103 local page dry-run over approved examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.pages.dry_run import run_page_dry_run  # noqa: E402
from runtime.pages.errors import PagePolicyError  # noqa: E402
from runtime.pages.policy import (  # noqa: E402
    default_example_roots,
    assert_no_forbidden_cli_args,
    ensure_approved_output_path,
)
from runtime.pages.report import report_to_json  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv if argv is not None else sys.argv[1:])
    try:
        assert_no_forbidden_cli_args(raw_args)
    except PagePolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--example-root", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--render-preview", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(raw_args)

    roots = [Path(item) for item in args.example_root]
    if args.all_examples or not roots:
        roots = list(default_example_roots())

    report = run_page_dry_run(
        roots,
        strict=args.strict,
        render=args.render_preview,
        enforce_approved_roots=True,
        allow_temp_roots=True,
    )
    payload = report_to_json(report)

    if args.output:
        try:
            output = ensure_approved_output_path(Path(args.output))
        except PagePolicyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        _write_output(output, report, payload, render_preview=args.render_preview)

    if args.json:
        print(payload, end="")
    else:
        print(f"report_id: {report.report_id}")
        print("mode: local_dry_run")
        print(f"pages_seen: {report.pages_seen}")
        print(f"pages_valid: {report.pages_valid}")
        print(f"pages_invalid: {report.pages_invalid}")
        for warning in report.warnings:
            print(f"warning: {warning}")
        for error in report.errors:
            print(f"error: {error.message}")

    if args.strict and (report.pages_invalid or report.errors):
        return 1
    return 0 if not report.errors else 1


def _write_output(output: Path, report, payload: str, *, render_preview: bool) -> None:
    if output.suffix.lower() == ".json":
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        return
    output.mkdir(parents=True, exist_ok=True)
    (output / "page_dry_run_report.json").write_text(payload, encoding="utf-8")
    if not render_preview:
        return
    for preview in report.preview_outputs:
        safe_id = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in preview.page_id)[:80]
        (output / f"{safe_id}.txt").write_text(preview.text_preview, encoding="utf-8")
        (output / f"{safe_id}.html").write_text(preview.html_preview, encoding="utf-8")
        (output / f"{safe_id}.preview.json").write_text(
            json.dumps(preview.json_preview, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    raise SystemExit(main())
