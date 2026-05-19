#!/usr/bin/env python3
"""Rebuild IA reviewed local index records from promotion previews."""

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
from runtime.public_index import PublicIndexStore  # noqa: E402
from runtime.source_observation.internet_archive_reviewed_index import (  # noqa: E402
    build_ia_reviewed_absence_packet,
    build_ia_reviewed_index_boundary_report,
    build_ia_reviewed_index_rebuild_report,
    build_ia_reviewed_object_packet,
    build_ia_reviewed_records_from_promotion_previews,
    load_default_ia_promotion_previews,
    load_ia_promotion_preview_file,
    load_ia_promotion_previews_from_review_queue,
    load_ia_reviewed_index_policy,
    rebuild_ia_reviewed_local_index,
    search_ia_reviewed_local_index,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local or temporary instance root.")
    parser.add_argument("--operator-token", help="Operator token required for --apply.")
    parser.add_argument("--from-promotion-previews", action="store_true", help="Use IA promotion preview records.")
    parser.add_argument("--from-promotion-report", help="Optional promotion dry-run report JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Build would-write reviewed records without mutating an instance.")
    parser.add_argument("--apply", action="store_true", help="Write reviewed records to the explicit local reviewed index.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional reviewed index rebuild report output path.")
    parser.add_argument("--boundary-output", help="Optional boundary report output path.")
    parser.add_argument("--search-query", action="append", default=[], help="Optional local reviewed index search proof query.")
    parser.add_argument("--object-id", help="Optional reviewed local record id for object proof.")
    parser.add_argument("--absence-query", action="append", default=[], help="Optional absence proof query.")
    args = parser.parse_args(argv)

    dry_run = not args.apply
    if args.apply and args.dry_run:
        print("error: choose either --dry-run or --apply", file=stderr)
        return 2
    if not args.from_promotion_previews and not args.from_promotion_report:
        print("error: --from-promotion-previews or --from-promotion-report is required", file=stderr)
        return 2
    if args.apply and not args.instance:
        print("error: --instance is required for --apply", file=stderr)
        return 2
    if args.apply and not args.operator_token:
        print("error: --operator-token is required for --apply", file=stderr)
        return 2

    try:
        policy = load_ia_reviewed_index_policy()
        previews = _load_promotion_previews(args)
        if not previews:
            raise RuntimeError("no IA promotion previews were available")
        reviewed_records = build_ia_reviewed_records_from_promotion_previews(previews, policy)
        write_scope = "dry_run_no_instance_mutation"
        proof_payload: dict[str, Any] = {
            "search_results": [],
            "object_packets": [],
            "absence_packets": [],
        }
        if dry_run:
            store_result = rebuild_ia_reviewed_local_index(None, reviewed_records, dry_run=True)
        else:
            _require_operator_token(args.instance, args.operator_token)
            paths = resolve_instance_paths(args.instance)
            write_scope = "temp_explicit_instance_only"
            with PublicIndexStore.open(paths.public_index_db) as store:
                store_result = rebuild_ia_reviewed_local_index(store, reviewed_records, dry_run=False)
                proof_payload = _build_proofs(store, reviewed_records, args)
        report = build_ia_reviewed_index_rebuild_report(reviewed_records, dry_run, store_result, write_scope)
        report.update(proof_payload)
        report["search_result_proof_passed"] = bool(proof_payload["search_results"]) if args.search_query else False
        report["object_packet_proof_passed"] = any(packet.get("found") is True for packet in proof_payload["object_packets"])
        report["absence_packet_proof_passed"] = (
            all(packet.get("absence_confirmed") is True for packet in proof_payload["absence_packets"])
            if args.absence_query
            else False
        )
        boundary = build_ia_reviewed_index_boundary_report(report)
    except Exception as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    if args.output:
        _write_json(Path(args.output), report)
    if args.boundary_output:
        _write_json(Path(args.boundary_output), boundary)

    payload = {"rebuild_report": report, "boundary_report": boundary}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print("IA reviewed local index rebuild", file=stdout)
        print(f"dry_run: {dry_run}", file=stdout)
        print(f"reviewed_record_count: {report['reviewed_record_count']}", file=stdout)
        print(f"reviewed_index_mutated: {str(report['reviewed_index_mutated']).lower()}", file=stdout)
    return 0


def _load_promotion_previews(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.from_promotion_report:
        return load_ia_promotion_preview_file(args.from_promotion_report)
    if args.instance:
        paths = resolve_instance_paths(args.instance)
        previews = load_ia_promotion_previews_from_review_queue(paths.review_queue_db)
        if previews:
            return previews
    return load_default_ia_promotion_previews()


def _build_proofs(store: PublicIndexStore, records: Sequence[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    search_results = []
    for query in args.search_query:
        search_results.extend(search_ia_reviewed_local_index(store, query))
    object_id = args.object_id or (str(records[0]["reviewed_record_id"]) if records else "")
    object_packets = [build_ia_reviewed_object_packet(store, object_id)] if object_id else []
    absence_packets = [build_ia_reviewed_absence_packet(store, query) for query in args.absence_query]
    return {
        "search_results": search_results,
        "object_packets": object_packets,
        "absence_packets": absence_packets,
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
