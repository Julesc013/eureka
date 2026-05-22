#!/usr/bin/env python3
"""Run the IA-02 bounded metadata-only live probe."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source_observation.internet_archive_live_probe import (  # noqa: E402
    load_live_probe_policy,
    normalize_live_probe_result,
    redact_live_probe_result,
    run_live_metadata_probe,
)


DEFAULT_USER_AGENT = "EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)"
DEFAULT_CONTACT = "local-operator"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approve-live", action="store_true", help="Approve the bounded IA-02 live metadata probe.")
    parser.add_argument("--query", help="Metadata search query. Defaults to IA-02 policy default_query.")
    parser.add_argument("--identifier", help="Optional exact IA identifier for one item metadata read.")
    parser.add_argument("--max-requests", type=int, help="Optional request cap, not exceeding policy.")
    parser.add_argument("--rows", type=int, help="Optional metadata search rows, not exceeding policy.")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="Descriptive User-Agent.")
    parser.add_argument("--contact", default=DEFAULT_CONTACT, help="Operator contact identifier.")
    parser.add_argument(
        "--kill-switch",
        choices=("enabled", "disabled"),
        default="enabled",
        help="IA-02 kill switch state checked before any live request.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--output", help="Optional path for redacted full report.")
    parser.add_argument("--redacted-output", help="Optional path for redacted live probe summary.")
    parser.add_argument("--boundary-output", help="Optional path for boundary report.")
    parser.add_argument("--dry-run", action="store_true", help="Build the request plan without network access.")
    args = parser.parse_args(argv)

    policy = load_live_probe_policy()
    dry_run = bool(args.dry_run or not args.approve_live)
    try:
        report = run_live_metadata_probe(
            policy,
            approve_live=bool(args.approve_live),
            dry_run=dry_run,
            query=args.query,
            identifier=args.identifier,
            rows=args.rows,
            max_requests=args.max_requests,
            client_label=args.user_agent,
            contact=args.contact,
            kill_switch_enabled=args.kill_switch == "enabled",
        )
    except (RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        _write_json(Path(args.output), report)
    if args.redacted_output:
        _write_json(Path(args.redacted_output), redact_live_probe_result(report))
    if args.boundary_output:
        _write_json(Path(args.boundary_output), report["boundary_report"])

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        summary = redact_live_probe_result(report)
        print("IA live metadata probe", file=stdout)
        print(f"dry_run: {report['dry_run']}", file=stdout)
        print(f"probe_status: {summary.get('probe_status')}", file=stdout)
        print(f"total_http_requests: {summary.get('total_http_requests')}", file=stdout)
        print(f"normalized_preview_count: {len(normalize_live_probe_result(report))}", file=stdout)
    return 0


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
