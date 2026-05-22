#!/usr/bin/env python3
"""Write IA evidence candidates into a provisional candidate index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.candidate_index import CandidateIndexStore  # noqa: E402
from runtime.local_appliance.config import load_instance_config  # noqa: E402
from runtime.local_appliance.instance import resolve_instance_paths  # noqa: E402
from runtime.local_operator import build_operator_auth_state, validate_operator_token, verify_operator_token  # noqa: E402
from runtime.source_observation.internet_archive_candidate_index import (  # noqa: E402
    build_ia_candidate_boundary_report,
    build_ia_candidate_write_report,
    build_ia_candidates_from_evidence,
    load_default_ia_evidence_candidates,
    load_ia_candidate_policy,
    load_ia_evidence_candidate_file,
    load_ia_evidence_candidates_from_ledger,
    write_ia_candidate_records,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local or temporary instance root.")
    parser.add_argument("--operator-token", help="Operator token required for --apply.")
    parser.add_argument("--from-evidence-ledger", action="store_true", help="Use IA evidence-ledger records.")
    parser.add_argument("--from-evidence-candidates", help="Optional JSON file containing IA evidence candidates.")
    parser.add_argument("--dry-run", action="store_true", help="Build would-write candidates without mutating an instance.")
    parser.add_argument("--apply", action="store_true", help="Write candidates to the explicit local candidate index.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional candidate write report output path.")
    parser.add_argument("--boundary-output", help="Optional boundary report output path.")
    parser.add_argument("--reset-demo-records", action="store_true", help="Reserved for a future explicit reset command.")
    args = parser.parse_args(argv)

    dry_run = not args.apply
    if args.apply and args.dry_run:
        print("error: choose either --dry-run or --apply", file=stderr)
        return 2
    if not args.from_evidence_ledger and not args.from_evidence_candidates:
        print("error: --from-evidence-ledger or --from-evidence-candidates is required", file=stderr)
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
        policy = load_ia_candidate_policy()
        evidence_candidates = _load_evidence_candidates(args)
        if not evidence_candidates:
            raise RuntimeError("no IA evidence candidates were available")
        candidates = build_ia_candidates_from_evidence(evidence_candidates, policy)
        write_scope = "dry_run_no_instance_mutation"
        store_result: dict[str, Any]
        if dry_run:
            store_result = write_ia_candidate_records(None, candidates, dry_run=True)
        else:
            _require_operator_token(args.instance, args.operator_token)
            paths = resolve_instance_paths(args.instance)
            write_scope = "temp_explicit_instance_only"
            store_path = paths.db_dir / "ia_candidate_index.json"
            store = CandidateIndexStore.open(store_path)
            store_result = write_ia_candidate_records(store, candidates, dry_run=False)
        report = build_ia_candidate_write_report(candidates, dry_run, store_result, write_scope)
        boundary = build_ia_candidate_boundary_report(report)
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
        print("IA candidate-index write", file=stdout)
        print(f"dry_run: {dry_run}", file=stdout)
        print(f"candidate_count: {report['candidate_count']}", file=stdout)
        print(f"candidate_index_mutated: {str(report['candidate_index_mutated']).lower()}", file=stdout)
    return 0


def _load_evidence_candidates(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.from_evidence_candidates:
        return load_ia_evidence_candidate_file(args.from_evidence_candidates)
    if args.instance:
        paths = resolve_instance_paths(args.instance)
        candidates = load_ia_evidence_candidates_from_ledger(paths.evidence_ledger_db)
        if candidates:
            return candidates
    return load_default_ia_evidence_candidates()


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
