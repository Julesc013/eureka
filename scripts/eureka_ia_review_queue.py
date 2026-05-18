#!/usr/bin/env python3
"""Write IA provisional candidates into the local review queue."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.config import load_instance_config  # noqa: E402
from runtime.local_appliance.instance import resolve_instance_paths  # noqa: E402
from runtime.local_operator import build_operator_auth_state, validate_operator_token, verify_operator_token  # noqa: E402
from runtime.review_queue import ReviewQueueStore  # noqa: E402
from runtime.source_observation.internet_archive_review import (  # noqa: E402
    apply_ia_review_decision,
    build_ia_review_boundary_report,
    build_ia_review_items_from_candidates,
    build_ia_review_queue_report,
    load_default_ia_candidate_records,
    load_ia_candidate_record_file,
    load_ia_candidates_from_index,
    load_ia_review_policy,
    write_ia_review_decisions,
    write_ia_review_items,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local or temporary instance root.")
    parser.add_argument("--operator-token", help="Operator token required for --apply.")
    parser.add_argument("--from-candidate-index", action="store_true", help="Use IA candidate-index records.")
    parser.add_argument("--from-candidates", help="Optional JSON file containing IA candidate records.")
    parser.add_argument("--decision", help="Optional deterministic IA-06 review decision to apply to every item.")
    parser.add_argument("--dry-run", action="store_true", help="Build review queue items without mutating an instance.")
    parser.add_argument("--apply", action="store_true", help="Write review queue items to the explicit local instance.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional review queue report output path.")
    parser.add_argument("--boundary-output", help="Optional boundary report output path.")
    args = parser.parse_args(argv)

    dry_run = not args.apply
    if args.apply and args.dry_run:
        print("error: choose either --dry-run or --apply", file=stderr)
        return 2
    if not args.from_candidate_index and not args.from_candidates:
        print("error: --from-candidate-index or --from-candidates is required", file=stderr)
        return 2
    if args.apply and not args.instance:
        print("error: --instance is required for --apply", file=stderr)
        return 2
    if args.apply and not args.operator_token:
        print("error: --operator-token is required for --apply", file=stderr)
        return 2

    try:
        policy = load_ia_review_policy()
        candidates = _load_candidates(args)
        if not candidates:
            raise RuntimeError("no IA candidate records were available")
        items = build_ia_review_items_from_candidates(candidates, policy)
        decisions = [apply_ia_review_decision(item, args.decision, policy) for item in items] if args.decision else []
        write_scope = "dry_run_no_instance_mutation"
        if dry_run:
            item_write = write_ia_review_items(None, items, dry_run=True)
            decision_write = write_ia_review_decisions(None, decisions, dry_run=True)
        else:
            _require_operator_token(args.instance, args.operator_token)
            paths = resolve_instance_paths(args.instance)
            write_scope = "temp_explicit_instance_only"
            with ReviewQueueStore.open(paths.review_queue_db) as store:
                item_write = write_ia_review_items(store, items, dry_run=False)
                decision_write = write_ia_review_decisions(store, decisions, dry_run=False)
        report = build_ia_review_queue_report(
            items,
            decisions,
            dry_run,
            {"item_write": item_write, "decision_write": decision_write},
            write_scope,
        )
        boundary = build_ia_review_boundary_report(report)
    except Exception as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    if args.output:
        _write_json(Path(args.output), report)
    if args.boundary_output:
        _write_json(Path(args.boundary_output), boundary)

    payload = {"review_report": report, "boundary_report": boundary}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print("IA review queue", file=stdout)
        print(f"dry_run: {dry_run}", file=stdout)
        print(f"review_item_count: {report['review_item_count']}", file=stdout)
        print(f"review_queue_mutated: {str(report['review_queue_mutated']).lower()}", file=stdout)
    return 0


def _load_candidates(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.from_candidates:
        return load_ia_candidate_record_file(args.from_candidates)
    if args.instance:
        paths = resolve_instance_paths(args.instance)
        candidates = load_ia_candidates_from_index(paths.db_dir / "ia_candidate_index.json")
        if candidates:
            return candidates
    return load_default_ia_candidate_records()


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
