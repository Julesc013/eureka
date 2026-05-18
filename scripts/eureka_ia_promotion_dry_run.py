#!/usr/bin/env python3
"""Build IA reviewed-record promotion previews without writing indexes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.config import load_instance_config  # noqa: E402
from runtime.local_appliance.instance import resolve_instance_paths  # noqa: E402
from runtime.local_operator import build_operator_auth_state, validate_operator_token, verify_operator_token  # noqa: E402
from runtime.review_queue import ReviewQueueStore  # noqa: E402
from runtime.source_observation.internet_archive_promotion import (  # noqa: E402
    build_ia_promotion_boundary_report,
    build_ia_promotion_dry_run_report,
    build_ia_promotion_previews,
    load_ia_promotion_dry_run_policy,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local or temporary instance root.")
    parser.add_argument("--operator-token", help="Operator token for the explicit instance.")
    parser.add_argument("--from-review-decisions", action="store_true", help="Use IA review decisions.")
    parser.add_argument("--from-review-report", help="Optional IA review queue report JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Reserved flag; promotion is always preview-only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional promotion dry-run report output path.")
    parser.add_argument("--boundary-output", help="Optional boundary report output path.")
    args = parser.parse_args(argv)

    if not args.from_review_decisions and not args.from_review_report:
        print("error: --from-review-decisions or --from-review-report is required", file=stderr)
        return 2
    if args.instance and args.operator_token:
        try:
            _require_operator_token(args.instance, args.operator_token)
        except Exception as exc:
            print(f"error: {exc}", file=stderr)
            return 1

    try:
        policy = load_ia_promotion_dry_run_policy()
        decisions = _load_review_decisions(args)
        previews = build_ia_promotion_previews(decisions, policy)
        report = build_ia_promotion_dry_run_report(previews, policy)
        boundary = build_ia_promotion_boundary_report(report)
    except Exception as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    if args.output:
        _write_json(Path(args.output), report)
    if args.boundary_output:
        _write_json(Path(args.boundary_output), boundary)

    payload = {"promotion_report": report, "boundary_report": boundary}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print("IA promotion dry-run", file=stdout)
        print(f"promotion_preview_count: {report['promotion_preview_count']}", file=stdout)
        print("reviewed_index_mutated: false", file=stdout)
        print("master_index_mutated: false", file=stdout)
    return 0


def _load_review_decisions(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.from_review_report:
        return _review_decisions_from_report(Path(args.from_review_report))
    if args.instance:
        paths = resolve_instance_paths(args.instance)
        if paths.review_queue_db.exists():
            with ReviewQueueStore.open(paths.review_queue_db) as store:
                store.init()
                decisions = store.list_decisions(limit=1000)
            values: list[dict[str, Any]] = []
            for decision in decisions:
                payload = dict(decision.payload)
                if payload.get("schema_version") == "ia_review_decision_payload.v0":
                    values.append(_decision_from_store_payload(decision.to_dict(), payload))
            return values
    return []


def _review_decisions_from_report(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    if not isinstance(payload, Mapping):
        return []
    for key in ("review_decisions", "decisions"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    report = payload.get("review_report")
    if isinstance(report, Mapping):
        value = report.get("review_decisions")
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    if payload.get("schema_version") == "ia_review_decision.v0":
        return [dict(payload)]
    return []


def _decision_from_store_payload(decision: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    source_refs = dict(payload.get("source_refs", {}) or {})
    return {
        "schema_version": "ia_review_decision.v0",
        "review_decision_id": str(decision.get("decision_id", "")),
        "review_item_id": str(decision.get("review_item_id", "")),
        "candidate_id": str(payload.get("ia_candidate_id", "")),
        "decision": str(payload.get("ia_decision", "")),
        "rationale": str(decision.get("reason", "")),
        "reviewer_kind": str(decision.get("decision_actor", "")),
        "creates_promotion_preview": bool(payload.get("creates_preview", False)),
        "accepted_truth": False,
        "reviewed_index_mutation_performed": False,
        "master_index_mutation_performed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "created_at": str(decision.get("created_at", "")),
        "candidate_snapshot": {
            "candidate_id": str(payload.get("ia_candidate_id", "")),
            "candidate_kind": "ia_candidate",
            "title": "IA promotion preview candidate",
            "summary": "Promotion preview reconstructed from durable review decision payload.",
            "source_locator": {},
            "evidence_ids": list(source_refs.get("evidence_refs", []) or []),
            "source_cache_record_ids": list(source_refs.get("source_cache_refs", []) or []),
            "observation_ids": list(source_refs.get("observation_refs", []) or []),
            "provenance": {"source_id": "internet_archive_metadata", "metadata_only": True},
            "uncertainty": ["reconstructed from durable review decision payload"],
            "limitations": ["preview-only reconstruction"],
            "risk_flags": [],
            "rights_flags": [],
        },
    }


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
