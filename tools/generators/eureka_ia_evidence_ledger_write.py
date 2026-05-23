#!/usr/bin/env python3
"""Write IA metadata source-cache records into evidence-ledger candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evidence.ledger import EvidenceLedgerStore  # noqa: E402
from runtime.local.appliance.config import load_instance_config  # noqa: E402
from runtime.local.appliance.instance import resolve_instance_paths  # noqa: E402
from runtime.local.operator import build_operator_auth_state, validate_operator_token, verify_operator_token  # noqa: E402
from runtime.source.observation.internet_archive_evidence import (  # noqa: E402
    build_ia_evidence_boundary_report,
    build_ia_evidence_candidate_records,
    build_ia_evidence_write_report,
    load_default_ia_source_cache_records,
    load_ia_evidence_policy,
    load_ia_source_cache_record_file,
    write_ia_evidence_candidates,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local or temporary instance root.")
    parser.add_argument("--operator-token", help="Operator token required for --apply.")
    parser.add_argument("--from-source-cache", action="store_true", help="Use IA source-cache records.")
    parser.add_argument("--from-source-cache-records", help="Optional JSON file containing IA source-cache records.")
    parser.add_argument("--dry-run", action="store_true", help="Build would-write evidence candidates without mutating an instance.")
    parser.add_argument("--apply", action="store_true", help="Write candidates to the explicit local evidence ledger.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional evidence write report output path.")
    parser.add_argument("--boundary-output", help="Optional boundary report output path.")
    parser.add_argument("--reset-demo-records", action="store_true", help="Reserved for a future explicit reset command.")
    args = parser.parse_args(argv)

    dry_run = not args.apply
    if args.apply and args.dry_run:
        print("error: choose either --dry-run or --apply", file=stderr)
        return 2
    if not args.from_source_cache and not args.from_source_cache_records:
        print("error: --from-source-cache or --from-source-cache-records is required", file=stderr)
        return 2
    if args.apply and not args.instance:
        print("error: --instance is required for --apply", file=stderr)
        return 2
    if args.apply and not args.operator_token:
        print("error: --operator-token is required for --apply", file=stderr)
        return 2
    if args.reset_demo_records:
        print("error: --reset-demo-records is reserved until a reviewed reset command exists", file=stderr)
        return 2

    try:
        policy = load_ia_evidence_policy()
        source_cache_records = (
            load_ia_source_cache_record_file(args.from_source_cache_records)
            if args.from_source_cache_records
            else load_default_ia_source_cache_records()
        )
        if not source_cache_records:
            raise RuntimeError("no IA source-cache records were available")
        candidates = build_ia_evidence_candidate_records(source_cache_records, policy)
        write_scope = "dry_run_no_instance_mutation"
        store_result: dict[str, Any]
        if dry_run:
            store_result = write_ia_evidence_candidates(None, candidates, dry_run=True)
        else:
            _require_operator_token(args.instance, args.operator_token)
            paths = resolve_instance_paths(args.instance)
            write_scope = "temp_explicit_instance_only"
            with EvidenceLedgerStore.open(paths.evidence_ledger_db) as store:
                store_result = write_ia_evidence_candidates(store, candidates, dry_run=False)
        report = build_ia_evidence_write_report(candidates, dry_run, store_result, write_scope)
        boundary = build_ia_evidence_boundary_report(report)
    except Exception as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    if args.output:
        _write_json(Path(args.output), report)
    if args.boundary_output:
        _write_json(Path(args.boundary_output), boundary)

    payload = {"write_report": report, "boundary_report": boundary}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print("IA evidence-ledger write", file=stdout)
        print(f"dry_run: {dry_run}", file=stdout)
        print(f"candidate_count: {report['candidate_count']}", file=stdout)
        print(f"evidence_ledger_write_performed: {str(report['evidence_ledger_write_performed']).lower()}", file=stdout)
    return 0


def _require_operator_token(instance: str, token: str | None) -> None:
    value = validate_operator_token(token or "")
    config = load_instance_config(Path(instance))
    auth_state = build_operator_auth_state(config)
    if not auth_state.configured:
        raise RuntimeError("operator token is not configured for the explicit instance")
    if not verify_operator_token(value, auth_state.token_hash, auth_state.token_salt):
        raise RuntimeError("operator token is invalid")


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
