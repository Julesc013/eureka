"""Local IA metadata bridge for Search Hunt, WorkUnits, and result lanes."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence

from runtime.candidate_index import CandidateIndexStore
from runtime.evidence_ledger import EvidenceLedgerStore
from runtime.public_index import PublicIndexStore
from runtime.review_queue import ReviewQueueStore
from runtime.search_hunt.records import SearchHuntSession
from runtime.source_cache import SourceCacheStore
from runtime.source_observation.ids import stable_digest
from runtime.source_observation.internet_archive_candidate_index import (
    build_ia_candidate_boundary_report,
    build_ia_candidate_write_report,
    build_ia_candidates_from_evidence,
    load_ia_candidate_policy,
    write_ia_candidate_records,
)
from runtime.source_observation.internet_archive_evidence import (
    build_ia_evidence_boundary_report,
    build_ia_evidence_candidate_records,
    build_ia_evidence_write_report,
    load_ia_evidence_policy,
    write_ia_evidence_candidates,
)
from runtime.source_observation.internet_archive_fixture_replay import replay_fixture_directory_report
from runtime.source_observation.internet_archive_promotion import (
    build_ia_promotion_boundary_report,
    build_ia_promotion_dry_run_report,
    build_ia_promotion_previews,
    load_ia_promotion_dry_run_policy,
)
from runtime.source_observation.internet_archive_review import (
    apply_ia_review_decision,
    build_ia_review_boundary_report,
    build_ia_review_items_from_candidates,
    build_ia_review_queue_report,
    load_ia_review_policy,
    write_ia_review_decisions,
    write_ia_review_items,
)
from runtime.source_observation.internet_archive_reviewed_index import (
    build_ia_reviewed_absence_packet,
    build_ia_reviewed_index_boundary_report,
    build_ia_reviewed_index_rebuild_report,
    build_ia_reviewed_object_packet,
    build_ia_reviewed_records_from_promotion_previews,
    load_ia_reviewed_index_policy,
    rebuild_ia_reviewed_local_index,
    search_ia_reviewed_local_index,
)
from runtime.source_observation.internet_archive_source_cache import (
    build_ia_source_cache_boundary_report,
    build_ia_source_cache_records,
    build_ia_source_cache_write_report,
    load_fixture_normalized_records,
    load_ia_source_cache_policy,
    write_ia_source_cache_records,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXED_CREATED_AT = "2026-05-21T00:00:00Z"
SOURCE_FAMILY = "internet_archive_metadata"
DEFAULT_QUERY = "sampleproject"
DEFAULT_POLICY_REF = "control/policies/ia_hunt_bridge_policy.json"
DEFAULT_INSTANCE_MARKER = "<temp-instance>"

IA_WORKUNIT_TYPES = (
    "ia_metadata_search",
    "ia_item_metadata_read",
    "ia_file_manifest_metadata",
    "ia_source_cache_write",
    "ia_evidence_candidate_write",
    "ia_candidate_index_write",
    "ia_review_queue_write",
    "ia_promotion_dry_run",
    "ia_reviewed_index_rebuild",
    "ia_result_lane_project",
)

IA_WORKUNIT_STATES = (
    "created",
    "queued",
    "running",
    "waiting_for_policy",
    "waiting_for_source_quota",
    "completed",
    "failed",
    "blocked",
    "cancelled",
)

WRITE_WORKUNIT_TYPES = {
    "ia_source_cache_write",
    "ia_evidence_candidate_write",
    "ia_candidate_index_write",
    "ia_review_queue_write",
    "ia_reviewed_index_rebuild",
}

BLOCKED_ACTIONS = (
    "run_source_probe",
    "live_ia_call",
    "download",
    "upload",
    "extract",
    "call_model_provider",
    "deploy",
    "mutate_master_index",
    "mutate_operator_instance",
)

DEFAULT_POLICY: dict[str, Any] = {
    "schema_version": "ia_hunt_bridge_policy.v0",
    "dry_run_default": True,
    "temp_instance_allowed": True,
    "operator_instance_mutation_default": False,
    "live_ia_calls_enabled_by_default": False,
    "live_ia_calls_require_explicit_policy": True,
    "source_cache_writes_allowed_only_in_temp_or_explicit_instance": True,
    "evidence_writes_allowed_only_in_temp_or_explicit_instance": True,
    "candidate_writes_allowed_only_in_temp_or_explicit_instance": True,
    "review_writes_allowed_only_in_temp_or_explicit_instance": True,
    "reviewed_index_rebuild_allowed_only_in_temp_or_explicit_instance": True,
    "master_index_mutation_enabled": False,
    "public_fanout_enabled": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
}


def create_ia_workunits_for_hunt(hunt_or_need: Mapping[str, Any] | Any, policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Create deterministic IA metadata WorkUnits for a Search Hunt or SearchNeed."""
    normalized_policy = normalize_policy(policy)
    hunt = _hunt_packet(hunt_or_need, _query_from_value(hunt_or_need))
    workunits: list[dict[str, Any]] = []
    for index, workunit_type in enumerate(IA_WORKUNIT_TYPES):
        writes_instance_state = workunit_type in WRITE_WORKUNIT_TYPES
        workunits.append(
            {
                "schema_version": "ia_hunt_workunit.v0",
                "workunit_id": "iawu_"
                + stable_digest(
                    {
                        "hunt_id": hunt["hunt_id"],
                        "workunit_type": workunit_type,
                        "index": index,
                    }
                ),
                "hunt_id": hunt["hunt_id"],
                "source_family": SOURCE_FAMILY,
                "workunit_type": workunit_type,
                "state": "queued",
                "input_ref": _input_ref_for_workunit(workunit_type, hunt),
                "output_ref": _output_ref_for_workunit(workunit_type, hunt),
                "policy_ref": str(normalized_policy.get("policy_ref", DEFAULT_POLICY_REF)),
                "dry_run": bool(normalized_policy.get("dry_run_default", True)),
                "writes_instance_state": writes_instance_state,
                "write_scope": "temp_or_explicit_instance_only" if writes_instance_state else "none",
                "blocked_actions": list(BLOCKED_ACTIONS),
                "created_at": FIXED_CREATED_AT,
                "completed_at": "",
                "limitations": [
                    "WorkUnit is local IA metadata orchestration only.",
                    "No live source probe, download, extraction, model call, deployment, or master-index mutation is enabled.",
                ],
            }
        )
    return workunits


def plan_ia_hunt_pipeline(query_or_need: str | Mapping[str, Any] | Any, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Plan the IA metadata bridge without mutating any store."""
    normalized_policy = normalize_policy(policy)
    query = _query_from_value(query_or_need)
    hunt = _hunt_packet(query_or_need, query)
    workunits = create_ia_workunits_for_hunt(hunt, normalized_policy)
    return {
        "schema_version": "ia_hunt_pipeline_plan.v0",
        "task": "IA-HUNT-BRIDGE-00",
        "query": query,
        "hunt": hunt,
        "workunits": workunits,
        "workunit_count": len(workunits),
        "source_family": SOURCE_FAMILY,
        "policy": normalized_policy,
        "dry_run": True,
        "from_fixtures": True,
        "from_ia_live_preview": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "deferred_actions": [
            "source probing",
            "downloads",
            "extraction",
            "model/provider calls",
            "deployment",
            "public fanout",
        ],
        "created_at": FIXED_CREATED_AT,
        "limitations": [
            "Plan is local and deterministic.",
            "Internet Archive live metadata calls remain disabled by default.",
        ],
    }


def run_ia_hunt_pipeline_dry_run(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Run the bridge in dry-run mode using committed IA metadata fixtures."""
    return _run_pipeline(plan, apply_to_temp=False, instance=None)


def run_ia_hunt_pipeline_temp_instance(
    plan: Mapping[str, Any],
    instance: str | Path | None,
    operator_token: str | None = None,
) -> dict[str, Any]:
    """Run the bridge against an explicit temporary instance path."""
    del operator_token
    if instance is None:
        with TemporaryDirectory(prefix="eureka-ia-hunt-bridge-") as tmp:
            return _run_pipeline(plan, apply_to_temp=True, instance=Path(tmp))
    return _run_pipeline(plan, apply_to_temp=True, instance=Path(instance))


def collect_ia_hunt_outputs(instance_or_outputs: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    """Collect IA Hunt bridge outputs from an output packet or temp instance."""
    if isinstance(instance_or_outputs, Mapping):
        outputs = dict(instance_or_outputs)
    else:
        path = Path(instance_or_outputs)
        payload_path = path / "ia_hunt_outputs.json"
        outputs = json.loads(payload_path.read_text(encoding="utf-8")) if payload_path.exists() else {}
    return {
        "schema_version": "ia_hunt_collected_outputs.v0",
        "query": str(outputs.get("query", "")),
        "source_cache_record_count": len(outputs.get("source_cache_records", []) or []),
        "evidence_candidate_count": len(outputs.get("evidence_candidates", []) or []),
        "candidate_count": len(outputs.get("candidate_records", []) or []),
        "review_item_count": len(outputs.get("review_items", []) or []),
        "promotion_preview_count": len(outputs.get("promotion_previews", []) or []),
        "reviewed_record_count": len(outputs.get("reviewed_records", []) or []),
        "workunit_count": len(outputs.get("workunits", []) or []),
        "outputs": outputs,
    }


def build_ia_hunt_result_lanes(outputs: Mapping[str, Any], projection_profile: str = "operator_workbench") -> dict[str, Any]:
    """Build Workbench result lanes from IA Hunt bridge outputs."""
    workbench = _workbench_result_lanes()
    packet = dict(outputs)
    query = str(packet.get("query") or DEFAULT_QUERY)
    workunits = [dict(item) for item in packet.get("workunits", []) or []]
    lanes = [
        workbench.build_result_lane_packet("reviewed_local_results", _reviewed_lane_items(packet.get("reviewed_records", []) or [])),
        workbench.build_result_lane_packet("local_candidate_results", _candidate_lane_items(packet.get("candidate_records", []) or [])),
        workbench.build_result_lane_packet("source_cache_hits", _source_cache_lane_items(packet.get("source_cache_records", []) or [])),
        workbench.build_result_lane_packet("ia_metadata_candidates", _ia_candidate_lane_items(packet.get("candidate_records", []) or [])),
        workbench.build_result_lane_packet("review_queue_items", _review_lane_items(packet.get("review_items", []) or [])),
        workbench.build_absence_lane(query, _absence_packet(query, packet)),
        workbench.build_result_lane_packet("near_misses", _near_miss_items(packet.get("candidate_records", []) or [])),
        workbench.build_blocked_action_lane(_blocked_policy_state(packet)),
        workbench.build_result_lane_packet("running_workunits", _workunit_lane_items(workunits)),
        workbench.build_deferred_deepening_lane(_deferred_workunit_items(workunits)),
        workbench.build_result_lane_packet("future_extraction_work", _future_extraction_items(workunits)),
    ]
    return workbench.build_result_lane_page_view(query, lanes, projection_profile)


def build_ia_hunt_boundary_report(outputs: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize the bridge side-effect and non-claim posture."""
    packet = dict(outputs)
    mode = str(packet.get("mode", "dry_run"))
    write_scope = str(packet.get("write_scope", "dry_run_no_instance_mutation"))
    source_cache_write = bool((packet.get("source_cache_report", {}) or {}).get("source_cache_write_performed", False))
    evidence_write = bool((packet.get("evidence_report", {}) or {}).get("evidence_ledger_write_performed", False))
    candidate_write = bool((packet.get("candidate_report", {}) or {}).get("candidate_index_mutated", False))
    review_write = bool((packet.get("review_report", {}) or {}).get("review_queue_mutated", False))
    reviewed_write = bool((packet.get("reviewed_index_report", {}) or {}).get("reviewed_index_mutated", False))
    return {
        "schema_version": "ia_hunt_bridge_boundary_report.v0",
        "task": "IA-HUNT-BRIDGE-00",
        "mode": mode,
        "passed": True,
        "violations": [],
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "source_cache_write_performed": source_cache_write,
        "source_cache_write_scope": write_scope if source_cache_write else "none",
        "evidence_write_performed": evidence_write,
        "evidence_write_scope": write_scope if evidence_write else "none",
        "candidate_index_mutated": candidate_write,
        "candidate_index_write_scope": write_scope if candidate_write else "none",
        "review_queue_mutated": review_write,
        "review_queue_write_scope": write_scope if review_write else "none",
        "reviewed_index_mutated": reviewed_write,
        "reviewed_index_write_scope": write_scope if reviewed_write else "none",
        "master_index_mutated": False,
        "operator_instance_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "full_archive_org_integration_claimed": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
    }


def normalize_policy(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return the bridge policy with strict false defaults for unsafe actions."""
    merged = dict(DEFAULT_POLICY)
    if policy:
        merged.update(dict(policy))
    merged.setdefault("policy_ref", DEFAULT_POLICY_REF)
    return merged


def _workbench_result_lanes() -> Any:
    from runtime.local_service import workbench_result_lanes

    return workbench_result_lanes


def _run_pipeline(plan: Mapping[str, Any], *, apply_to_temp: bool, instance: Path | None) -> dict[str, Any]:
    query = str(plan.get("query") or DEFAULT_QUERY)
    workunits = [dict(item) for item in plan.get("workunits", []) or []]
    dry_run = not apply_to_temp
    write_scope = "temp_instance" if apply_to_temp else "dry_run_no_instance_mutation"
    instance_root = instance.resolve() if instance else None

    fixture_report = replay_fixture_directory_report()
    normalized_records = load_fixture_normalized_records()
    source_cache_policy = load_ia_source_cache_policy()
    source_cache_records = build_ia_source_cache_records(normalized_records, source_cache_policy)

    evidence_policy = load_ia_evidence_policy()
    evidence_candidates = build_ia_evidence_candidate_records(source_cache_records, evidence_policy)

    candidate_policy = load_ia_candidate_policy()
    candidate_records = build_ia_candidates_from_evidence(evidence_candidates, candidate_policy)

    review_policy = load_ia_review_policy()
    review_items = build_ia_review_items_from_candidates(candidate_records, review_policy)
    review_decisions = [
        apply_ia_review_decision(item, "approve_for_reviewed_index_dry_run", review_policy)
        for item in review_items
    ]

    promotion_policy = load_ia_promotion_dry_run_policy()
    promotion_previews = build_ia_promotion_previews(review_decisions, promotion_policy)

    reviewed_policy = load_ia_reviewed_index_policy()
    reviewed_records = build_ia_reviewed_records_from_promotion_previews(promotion_previews, reviewed_policy)

    store_results = _write_store_results(
        instance_root,
        dry_run,
        source_cache_records,
        evidence_candidates,
        candidate_records,
        review_items,
        review_decisions,
        reviewed_records,
        query,
    )

    source_cache_report = build_ia_source_cache_write_report(
        source_cache_records,
        dry_run=dry_run,
        store_result=store_results["source_cache"],
        write_scope=write_scope,
    )
    evidence_report = build_ia_evidence_write_report(
        evidence_candidates,
        dry_run,
        store_results["evidence"],
        write_scope,
    )
    candidate_report = build_ia_candidate_write_report(
        candidate_records,
        dry_run,
        store_results["candidate"],
        write_scope,
    )
    review_report = build_ia_review_queue_report(
        review_items,
        review_decisions,
        dry_run,
        {"item_write": store_results["review_items"], "decision_write": store_results["review_decisions"]},
        write_scope,
    )
    promotion_report = build_ia_promotion_dry_run_report(promotion_previews, promotion_policy)
    reviewed_index_report = build_ia_reviewed_index_rebuild_report(
        reviewed_records,
        dry_run,
        store_results["reviewed_index"],
        write_scope,
    )
    reviewed_index_report.update(store_results["reviewed_proofs"])

    completed_workunits = [_complete_workunit(item, apply_to_temp) for item in workunits]
    outputs: dict[str, Any] = {
        "schema_version": "ia_hunt_pipeline_outputs.v0",
        "task": "IA-HUNT-BRIDGE-00",
        "mode": "temp_instance" if apply_to_temp else "dry_run",
        "dry_run": dry_run,
        "write_scope": write_scope,
        "instance_root": DEFAULT_INSTANCE_MARKER if apply_to_temp else "",
        "query": query,
        "hunt": dict(plan.get("hunt", {}) or {}),
        "workunits": completed_workunits,
        "source_cache_records": source_cache_records,
        "evidence_candidates": evidence_candidates,
        "candidate_records": candidate_records,
        "review_items": review_items,
        "review_decisions": review_decisions,
        "promotion_previews": promotion_previews,
        "reviewed_records": reviewed_records,
        "fixture_report": {
            "schema_version": fixture_report.get("schema_version"),
            "record_count": len(fixture_report.get("normalized_records", []) or []),
            "boundary_reports": fixture_report.get("boundary_reports", []),
        },
        "source_cache_report": source_cache_report,
        "evidence_report": evidence_report,
        "candidate_report": candidate_report,
        "review_report": review_report,
        "promotion_report": promotion_report,
        "reviewed_index_report": reviewed_index_report,
        "boundary_reports": [
            build_ia_source_cache_boundary_report(source_cache_report),
            build_ia_evidence_boundary_report(evidence_report),
            build_ia_candidate_boundary_report(candidate_report),
            build_ia_review_boundary_report(review_report),
            build_ia_promotion_boundary_report(promotion_report),
            build_ia_reviewed_index_boundary_report(reviewed_index_report),
        ],
    }
    outputs["boundary_report"] = build_ia_hunt_boundary_report(outputs)
    outputs["result_lane_page"] = build_ia_hunt_result_lanes(outputs, "operator_workbench")
    if instance_root is not None:
        instance_root.mkdir(parents=True, exist_ok=True)
        (instance_root / "ia_hunt_outputs.json").write_text(json.dumps(outputs, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return outputs


def _write_store_results(
    instance_root: Path | None,
    dry_run: bool,
    source_cache_records: Sequence[Mapping[str, Any]],
    evidence_candidates: Sequence[Mapping[str, Any]],
    candidate_records: Sequence[Mapping[str, Any]],
    review_items: Sequence[Mapping[str, Any]],
    review_decisions: Sequence[Mapping[str, Any]],
    reviewed_records: Sequence[Mapping[str, Any]],
    query: str,
) -> dict[str, Any]:
    if dry_run:
        return {
            "source_cache": write_ia_source_cache_records(None, source_cache_records, dry_run=True),
            "evidence": write_ia_evidence_candidates(None, evidence_candidates, dry_run=True),
            "candidate": write_ia_candidate_records(None, candidate_records, dry_run=True),
            "review_items": write_ia_review_items(None, review_items, dry_run=True),
            "review_decisions": write_ia_review_decisions(None, review_decisions, dry_run=True),
            "reviewed_index": rebuild_ia_reviewed_local_index(None, reviewed_records, dry_run=True),
            "reviewed_proofs": {"search_results": [], "object_packets": [], "absence_packets": []},
        }
    if instance_root is None:
        raise ValueError("instance path is required for temp-instance apply")
    db_dir = instance_root / "stores"
    db_dir.mkdir(parents=True, exist_ok=True)
    with SourceCacheStore.open(db_dir / "source_cache.sqlite") as source_store:
        source_result = write_ia_source_cache_records(source_store, source_cache_records, dry_run=False)
    with EvidenceLedgerStore.open(db_dir / "evidence_ledger.sqlite") as evidence_store:
        evidence_result = write_ia_evidence_candidates(evidence_store, evidence_candidates, dry_run=False)
    candidate_store = CandidateIndexStore.open(db_dir / "candidate_index.json")
    candidate_result = write_ia_candidate_records(candidate_store, candidate_records, dry_run=False)
    with ReviewQueueStore.open(db_dir / "review_queue.sqlite") as review_store:
        review_item_result = write_ia_review_items(review_store, review_items, dry_run=False)
        review_decision_result = write_ia_review_decisions(review_store, review_decisions, dry_run=False)
    with PublicIndexStore.open(db_dir / "public_index.sqlite") as public_store:
        reviewed_result = rebuild_ia_reviewed_local_index(public_store, reviewed_records, dry_run=False)
        object_id = str(reviewed_records[0].get("reviewed_record_id", "")) if reviewed_records else ""
        proofs = {
            "search_results": search_ia_reviewed_local_index(public_store, query),
            "object_packets": [build_ia_reviewed_object_packet(public_store, object_id)] if object_id else [],
            "absence_packets": [build_ia_reviewed_absence_packet(public_store, "definitely-not-present-ia-hunt-bridge")],
        }
    return {
        "source_cache": source_result,
        "evidence": evidence_result,
        "candidate": candidate_result,
        "review_items": review_item_result,
        "review_decisions": review_decision_result,
        "reviewed_index": reviewed_result,
        "reviewed_proofs": proofs,
    }


def _hunt_packet(value: Mapping[str, Any] | Any, query: str) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        source = dict(value.to_dict())
    elif isinstance(value, Mapping):
        source = dict(value)
    else:
        source = {}
    hunt_id = str(source.get("hunt_id") or source.get("id") or "")
    if not hunt_id:
        hunt = SearchHuntSession.new(query=query)
        source = hunt.to_dict()
        hunt_id = str(source.get("id", ""))
    return {
        "schema_version": "ia_hunt_bridge_hunt_ref.v0",
        "hunt_id": hunt_id,
        "search_need_id": str(source.get("search_need_id") or source.get("need_id") or ""),
        "query": str(source.get("query") or query),
        "state": str(source.get("state") or "created"),
        "source": "search_hunt",
        "accepted_truth_created": False,
        "source_probe_executed": False,
        "live_ia_call_performed": False,
    }


def _query_from_value(value: Any) -> str:
    if isinstance(value, str):
        return value or DEFAULT_QUERY
    if isinstance(value, Mapping):
        for key in ("query", "query_text", "raw_query"):
            if value.get(key):
                return str(value[key])
    if hasattr(value, "query"):
        return str(getattr(value, "query") or DEFAULT_QUERY)
    return DEFAULT_QUERY


def _input_ref_for_workunit(workunit_type: str, hunt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "hunt_id": str(hunt.get("hunt_id", "")),
        "query": str(hunt.get("query", "")),
        "input_kind": "fixture_metadata" if workunit_type in {"ia_metadata_search", "ia_item_metadata_read", "ia_file_manifest_metadata"} else "local_bridge_output",
    }


def _output_ref_for_workunit(workunit_type: str, hunt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "hunt_id": str(hunt.get("hunt_id", "")),
        "output_kind": workunit_type.replace("ia_", ""),
        "artifact_ref": f"ia_hunt_bridge/{hunt.get('hunt_id', '')}/{workunit_type}",
    }


def _complete_workunit(workunit: Mapping[str, Any], apply_to_temp: bool) -> dict[str, Any]:
    item = dict(workunit)
    item["state"] = "completed"
    item["completed_at"] = FIXED_CREATED_AT
    item["dry_run"] = not apply_to_temp
    if item.get("workunit_type") in WRITE_WORKUNIT_TYPES:
        item["writes_instance_state"] = bool(apply_to_temp)
        item["write_scope"] = "temp_instance" if apply_to_temp else "dry_run_no_instance_mutation"
    return item


def _reviewed_lane_items(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item_id": str(record.get("reviewed_record_id", "")),
            "title": str(record.get("title", "")),
            "summary": str(record.get("summary", "")),
            "source_record_ids": list(record.get("source_cache_record_ids", []) or []),
            "evidence_refs": list(record.get("evidence_ids", []) or []),
            "operator_notes": "IA reviewed local result is temp/local only and not master/public truth.",
            "limitations": list(record.get("limitations", []) or []),
            "uncertainty": list(record.get("uncertainty", []) or []),
            "provenance": dict(record.get("provenance", {}) or {}),
        }
        for record in records[:8]
    ]


def _candidate_lane_items(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item_id": str(record.get("candidate_id", "")),
            "title": str(record.get("candidate_title", "")),
            "summary": str(record.get("candidate_summary", "")),
            "candidate_refs": [str(record.get("candidate_id", ""))],
            "evidence_refs": list(record.get("evidence_ids", []) or []),
            "operator_notes": "Candidate requires review and does not create accepted truth.",
            "limitations": list(record.get("limitations", []) or []),
            "uncertainty": list(record.get("uncertainty", []) or []),
            "provenance": dict(record.get("provenance", {}) or {}),
        }
        for record in records[:8]
    ]


def _source_cache_lane_items(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item_id": str(record.get("record_id", "")),
            "title": str(record.get("title_candidate") or record.get("endpoint_class") or "IA source-cache record"),
            "summary": str((record.get("normalized_summary", {}) or {}).get("summary", "IA metadata source-cache record.")),
            "source_cache_entry_ids": [str(record.get("record_id", ""))],
            "operator_notes": "Source-cache hit is metadata observation only.",
            "limitations": list(record.get("limitation_flags", []) or []),
            "uncertainty": ["Source metadata is not accepted truth."],
            "provenance": {"source_kind": str(record.get("source_kind", "")), "source_id": str(record.get("source_id", ""))},
        }
        for record in records[:8]
    ]


def _ia_candidate_lane_items(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item_id": "ia-lane-" + str(record.get("candidate_id", "")),
            "title": str(record.get("candidate_title", "")),
            "summary": str(record.get("candidate_summary", "")),
            "candidate_refs": [str(record.get("candidate_id", ""))],
            "evidence_refs": list(record.get("evidence_ids", []) or []),
            "operator_notes": "IA metadata candidate is source-provided metadata requiring review.",
            "limitations": list(record.get("limitations", []) or []),
            "uncertainty": list(record.get("uncertainty", []) or []),
            "provenance": dict(record.get("provenance", {}) or {}),
        }
        for record in records[:8]
    ]


def _review_lane_items(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item_id": str(record.get("review_item_id", "")),
            "title": str(record.get("title", "")),
            "summary": str(record.get("summary", "")),
            "review_refs": [str(record.get("review_item_id", ""))],
            "candidate_refs": [str(record.get("candidate_id", ""))],
            "operator_notes": "Review queue item is local review work only.",
            "limitations": list(record.get("limitations", []) or []),
            "uncertainty": list(record.get("uncertainty", []) or []),
            "provenance": dict(record.get("provenance", {}) or {}),
        }
        for record in records[:8]
    ]


def _absence_packet(query: str, outputs: Mapping[str, Any]) -> dict[str, Any]:
    result_count = len(outputs.get("reviewed_records", []) or [])
    return {
        "absence_id": "ia-hunt-absence-" + stable_digest({"query": query, "result_count": result_count}),
        "summary": "Known absence is bounded to checked local IA Hunt bridge layers.",
        "checked_layers": ["reviewed_local_results", "source_cache_hits", "ia_metadata_candidates"],
    }


def _near_miss_items(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for record in records:
        risk_flags = {str(item) for item in record.get("risk_flags", []) or []}
        if record.get("candidate_kind") == "ia_near_miss_candidate" or risk_flags:
            items.append(
                {
                    "item_id": "near-miss-" + str(record.get("candidate_id", "")),
                    "title": str(record.get("candidate_title", "")),
                    "summary": str(record.get("candidate_summary", "")),
                    "candidate_refs": [str(record.get("candidate_id", ""))],
                    "operator_notes": "Near miss is review context only.",
                    "limitations": list(record.get("limitations", []) or []),
                    "uncertainty": list(record.get("uncertainty", []) or []),
                }
            )
    return items[:8]


def _blocked_policy_state(outputs: Mapping[str, Any]) -> dict[str, str]:
    del outputs
    return {
        "run_source_probe": "Blocked: live source probes are not enabled by IA-HUNT-BRIDGE-00.",
        "live_ia_call": "Blocked: live IA calls remain disabled by default.",
        "download": "Blocked: downloads are out of scope.",
        "extract": "Blocked: extraction is deferred.",
        "call_model_provider": "Blocked: no model/provider calls are enabled.",
        "deploy": "Blocked: deployment and public fanout are out of scope.",
        "mutate_master_index": "Blocked: master index mutation is disabled.",
    }


def _workunit_lane_items(workunits: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item_id": str(item.get("workunit_id", "")),
            "title": str(item.get("workunit_type", "")).replace("_", " "),
            "summary": f"IA Hunt WorkUnit state: {item.get('state', '')}.",
            "workunit_refs": [str(item.get("workunit_id", ""))],
            "operator_notes": "WorkUnit is local orchestration state, not product truth.",
            "limitations": list(item.get("limitations", []) or []),
        }
        for item in workunits
    ]


def _deferred_workunit_items(workunits: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "workunit_id": str(item.get("workunit_id", "")),
            "title": str(item.get("workunit_type", "")).replace("_", " "),
            "summary": "Future deepening remains gated by policy.",
        }
        for item in workunits
        if item.get("workunit_type") in {"ia_metadata_search", "ia_item_metadata_read", "ia_file_manifest_metadata"}
    ]


def _future_extraction_items(workunits: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item_id": "future-extraction-ia-hunt",
            "title": "Future extraction remains disabled",
            "summary": "IA Hunt bridge only prepares metadata WorkUnits; extraction is deferred to later governed work.",
            "workunit_refs": [str(item.get("workunit_id", "")) for item in workunits if item.get("workunit_type") == "ia_file_manifest_metadata"],
            "operator_notes": "No extraction was executed.",
        }
    ]


__all__ = [
    "BLOCKED_ACTIONS",
    "DEFAULT_POLICY",
    "IA_WORKUNIT_STATES",
    "IA_WORKUNIT_TYPES",
    "build_ia_hunt_boundary_report",
    "build_ia_hunt_result_lanes",
    "collect_ia_hunt_outputs",
    "create_ia_workunits_for_hunt",
    "normalize_policy",
    "plan_ia_hunt_pipeline",
    "run_ia_hunt_pipeline_dry_run",
    "run_ia_hunt_pipeline_temp_instance",
]
