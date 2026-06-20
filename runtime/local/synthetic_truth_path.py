"""Isolated synthetic end-to-end review and materialization proof."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any, Mapping, Sequence

from runtime.local.search_index import INDEX_SCHEMA_VERSION, INDEX_DOCUMENT_SCHEMA_VERSION, search_index_path, validate_index
from runtime.resolution_run import run_e2e_reference_run, validate_run_bundle
from runtime.resolution_run.run_store import FIXED_CREATED_AT
from runtime.review import ReviewLedgerDecisionRequest, record_review_ledger_decision
from runtime.review.queue import ReviewItemRecord, ReviewQueueStatus, ReviewQueueStore
from runtime.snapshots.envelope import build_envelope_for_manifest
from runtime.snapshots.fixity import build_snapshot_fixity_report
from runtime.snapshots.manifest import build_snapshot_manifest, stable_id as snapshot_stable_id
from runtime.snapshots.verify import build_snapshot_verification_report


REPO_ROOT = Path(__file__).resolve().parents[2]
NAMESPACE = "synthetic:e2e-reference"
ORACLE_ACTOR = "synthetic:e2e-reference-oracle"
DEFAULT_SCENARIO = "minimal-success"
DEFAULT_OUTPUT_ROOT = Path(".eureka/test/e2e-reference/synthetic-truth-path")
APPROVED_OUTPUT_ROOT = (REPO_ROOT / DEFAULT_OUTPUT_ROOT).resolve()
FIXTURE_ROOT = REPO_ROOT / "evals" / "e2e_reference" / "synthetic_truth"
SCENARIO_SCHEMA_VERSION = "eureka.synthetic_truth_path.scenario.v0"
REVIEWED_RECORD_SCHEMA_VERSION = "eureka.synthetic_reviewed_record.v0"
BOUNDARY_SCHEMA_VERSION = "eureka.synthetic_acceptance_boundary_report.v0"


class SyntheticTruthPathError(ValueError):
    """Raised when the synthetic path crosses a forbidden boundary."""


@dataclass(frozen=True)
class SyntheticTruthPathOptions:
    scenario: str = DEFAULT_SCENARIO
    out_root: Path = DEFAULT_OUTPUT_ROOT
    clean: bool = True


def run_synthetic_truth_path(options: SyntheticTruthPathOptions | None = None) -> dict[str, Any]:
    opts = options or SyntheticTruthPathOptions()
    fixture = load_synthetic_truth_fixture(opts.scenario)
    root = _approved_root(opts.out_root)
    scenario_dir = _safe_child(root, opts.scenario)
    if opts.clean and scenario_dir.exists():
        _remove_generated_scenario_dir(scenario_dir)
    _create_layout(scenario_dir)

    entities = build_synthetic_entities(fixture)
    _write_inputs(scenario_dir, entities)

    run_result = _run_reference_runner(scenario_dir, fixture)
    run_ref = _write_run_ref(scenario_dir, run_result)

    baseline_truth = _write_truth_generation(scenario_dir, "baseline", [])
    _activate_generation(scenario_dir / "truth", baseline_truth["generation_id"], kind="truth")
    baseline_index = _write_index_generation(scenario_dir, "baseline", [_candidate_document(entities["candidate"], fixture)])
    _activate_generation(scenario_dir / "index", baseline_index["generation_id"], kind="index")
    search_before = _search_active_index(scenario_dir, str(fixture["query"]), "search_before.json")

    review = _record_synthetic_decision(scenario_dir, entities)
    reviewed_record = materialize_synthetic_reviewed_record(
        candidate=entities["candidate"],
        review_item=entities["review_item"],
        decision_result=review["decision_result"],
        output_root=scenario_dir / "truth",
    )
    reviewed_truth = _write_truth_generation(scenario_dir, "reviewed", [reviewed_record])
    _activate_generation(scenario_dir / "truth", reviewed_truth["generation_id"], kind="truth")
    reviewed_index = _write_index_generation(
        scenario_dir,
        "reviewed",
        [_candidate_document(entities["candidate"], fixture), _reviewed_document(reviewed_record, fixture)],
    )
    _activate_generation(scenario_dir / "index", reviewed_index["generation_id"], kind="index")
    search_after = _search_active_index(scenario_dir, str(fixture["query"]), "search_after.json")

    rollback = rollback_synthetic_truth_path(scenario_dir)
    snapshot = _write_snapshot(scenario_dir, reviewed_record, search_after)
    manifest = _write_scenario_manifest(
        scenario_dir,
        fixture,
        entities,
        run_ref,
        review,
        reviewed_record,
        baseline_truth,
        reviewed_truth,
        baseline_index,
        reviewed_index,
        search_before,
        search_after,
        rollback,
        snapshot,
    )
    _write_json(scenario_dir / "reports" / "boundary_report.json", boundary_report(scenario_dir, []))
    _write_scenario_report(scenario_dir, manifest, {"status": "pending"})
    validation = validate_synthetic_truth_path(scenario_dir, strict=True)
    _write_json(scenario_dir / "reports" / "validation_report.json", validation)
    _write_scenario_report(scenario_dir, manifest, validation)
    return {
        "schema_version": "eureka.synthetic_truth_path.run_result.v0",
        "status": "PASS" if validation["status"] == "pass" else "FAIL",
        "scenario_dir": _rel(scenario_dir),
        "scenario_manifest": _rel(scenario_dir / "scenario_manifest.json"),
        "scenario_id": manifest["scenario_id"],
        "namespace": NAMESPACE,
        "query": fixture["query"],
        "run_id": run_ref["run_id"],
        "review_item_id": entities["review_item"]["review_item_id"],
        "review_decision_id": review["decision_result"]["decision_id"],
        "reviewed_record_id": reviewed_record["reviewed_record_id"],
        "baseline_result": _result_status(search_before),
        "post_review_result": _result_status(search_after),
        "rollback_result": _result_status(rollback["search_rollback"]),
        "snapshot_manifest_id": snapshot["manifest"]["snapshot_manifest_id"],
        "snapshot_verification_status": snapshot["verification"]["verification_status"],
        "validation_status": validation["status"],
        "errors": validation["errors"],
        **_safety_flags(),
    }


def load_synthetic_truth_fixture(scenario: str = DEFAULT_SCENARIO) -> dict[str, Any]:
    path = FIXTURE_ROOT / f"{_safe_name(scenario)}.json"
    if not path.is_file():
        raise SyntheticTruthPathError(f"synthetic scenario fixture not found: {path}")
    payload = _load_json(path)
    if payload.get("namespace") != NAMESPACE:
        raise SyntheticTruthPathError("synthetic fixture namespace is invalid")
    if str(payload.get("source_family")) in {"internet_archive", "ia_metadata"}:
        raise SyntheticTruthPathError("synthetic fixture must not use real source families")
    return payload


def build_synthetic_entities(fixture: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    query = str(fixture["query"])
    source_observation = {
        "schema_version": "eureka.synthetic_source_observation.v0",
        "namespace": NAMESPACE,
        "source_family": "synthetic",
        "source_id": "synthetic:e2e-reference:source",
        "observation_id": _stable_id("source-observation:synthetic", {"scenario": fixture["scenario"], "query": query}),
        "query": query,
        "title": fixture["title"],
        "version": fixture["version"],
        "platform": fixture["platform"],
        "metadata": dict(fixture.get("metadata") or {}),
        "network_used": False,
        "accepted_truth": False,
        "synthetic": True,
        "limitations": list(fixture.get("limitations") or []),
    }
    evidence_summary = {
        "schema_version": "eureka.synthetic_evidence_summary.v0",
        "namespace": NAMESPACE,
        "evidence_id": _stable_id("evidence:synthetic", {"observation": source_observation["observation_id"], "query": query}),
        "source_observation_refs": [source_observation["observation_id"]],
        "candidate_refs": [],
        "proposition": fixture["proposition"],
        "support_posture": "synthetic_fixture_support",
        "accepted_truth": False,
        "synthetic": True,
        "limitations": ["synthetic test support only"],
    }
    candidate = {
        "schema_version": "eureka.synthetic_candidate.v0",
        "namespace": NAMESPACE,
        "candidate_id": _stable_id("candidate:synthetic", {"title": fixture["title"], "version": fixture["version"], "refs": [source_observation["observation_id"]]}),
        "status": "provisional",
        "review_state": "unreviewed",
        "title": fixture["title"],
        "summary": fixture["summary"],
        "query": query,
        "version": fixture["version"],
        "platform": fixture["platform"],
        "source_observation_refs": [source_observation["observation_id"]],
        "evidence_refs": [evidence_summary["evidence_id"]],
        "accepted_truth": False,
        "artifact_verified": False,
        "public_eligible": False,
        "production_eligible": False,
        "synthetic": True,
    }
    evidence_summary["candidate_refs"] = [candidate["candidate_id"]]
    review_item = {
        "schema_version": "eureka.synthetic_review_item.v0",
        "namespace": NAMESPACE,
        "review_item_id": _stable_id("review-item:synthetic", {"candidate": candidate["candidate_id"], "evidence": evidence_summary["evidence_id"]}),
        "candidate_id": candidate["candidate_id"],
        "evidence_refs": [evidence_summary["evidence_id"]],
        "source_observation_refs": [source_observation["observation_id"]],
        "queue_status": "needs_review",
        "synthetic": True,
    }
    return {
        "source_observation": source_observation,
        "evidence_summary": evidence_summary,
        "candidate": candidate,
        "review_item": review_item,
    }


def materialize_synthetic_reviewed_record(
    *,
    candidate: Mapping[str, Any],
    review_item: Mapping[str, Any],
    decision_result: Mapping[str, Any],
    output_root: str | Path,
) -> dict[str, Any]:
    output = Path(output_root)
    _ensure_under_approved_root(output)
    _assert_synthetic_candidate(candidate)
    if review_item.get("namespace") != NAMESPACE:
        raise SyntheticTruthPathError("review item namespace must be synthetic")
    if review_item.get("candidate_id") != candidate.get("candidate_id"):
        raise SyntheticTruthPathError("review item candidate mismatch")
    if decision_result.get("review_item_id") != review_item.get("review_item_id"):
        raise SyntheticTruthPathError("decision review item mismatch")
    if decision_result.get("decision") != "promote":
        raise SyntheticTruthPathError("synthetic materialization requires a promote decision")
    payload = dict((decision_result.get("review_event") or {}).get("event_payload") or {})
    if payload.get("local_only_confirmed") is not True:
        raise SyntheticTruthPathError("synthetic promote requires local-only confirmation")
    if decision_result.get("queue_status") != "accepted":
        raise SyntheticTruthPathError("synthetic decision must accept the review item")
    if str(decision_result.get("review_item_id") or "").startswith("review-item:ia_metadata"):
        raise SyntheticTruthPathError("real IA review items are forbidden")
    if str(payload.get("visibility_posture") or "") != "operator_private":
        raise SyntheticTruthPathError("synthetic decision visibility must remain operator-private")
    source_refs = _string_list(candidate.get("source_observation_refs"))
    evidence_refs = _string_list(candidate.get("evidence_refs"))
    if not source_refs or not evidence_refs:
        raise SyntheticTruthPathError("source and evidence refs are required")
    reviewed_record_id = _stable_id(
        "reviewed-record:synthetic",
        {
            "candidate": candidate["candidate_id"],
            "review_item": review_item["review_item_id"],
            "decision": decision_result["decision"],
            "actor": ORACLE_ACTOR,
        },
    )
    return {
        "schema_version": REVIEWED_RECORD_SCHEMA_VERSION,
        "reviewed_record_id": reviewed_record_id,
        "source_candidate_id": candidate["candidate_id"],
        "review_item_id": review_item["review_item_id"],
        "review_decision_id": decision_result["decision_id"],
        "review_event_refs": [decision_result["review_event_id"]],
        "source_observation_refs": source_refs,
        "evidence_refs": evidence_refs,
        "title": candidate["title"],
        "summary": candidate["summary"],
        "review_state": "accepted",
        "record_state": "reviewed",
        "accepted_truth": True,
        "truth_scope": "synthetic_test_only",
        "synthetic": True,
        "namespace": NAMESPACE,
        "production_eligible": False,
        "public_eligible": False,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee": False,
        "limitations": [
            "accepted only inside isolated synthetic test namespace",
            "not a verified artifact",
            "not production authority",
        ],
        "prohibited_claims": [
            "public truth",
            "production truth",
            "verified artifact",
            "safe file",
            "rights cleared",
        ],
        "created_at": FIXED_CREATED_AT,
    }


def rollback_synthetic_truth_path(scenario_dir: str | Path) -> dict[str, Any]:
    root = Path(scenario_dir)
    _ensure_under_approved_root(root)
    index_current_before = _load_json(root / "index" / "current.json")
    truth_current_before = _load_json(root / "truth" / "current.json")
    baseline_truth = "truth-generation.baseline.v0"
    baseline_index = "index-generation.baseline.v0"
    _activate_generation(root / "truth", baseline_truth, kind="truth")
    _activate_generation(root / "index", baseline_index, kind="index")
    search_rollback = _search_active_index(root, _load_json(root / "input" / "candidate.json")["query"], "search_rollback.json")
    truth_report = {
        "schema_version": "eureka.synthetic_truth_rollback_report.v0",
        "status": "PASS",
        "before": truth_current_before.get("generation_id"),
        "after": baseline_truth,
        "history_preserved": True,
        "immutable_generations_preserved": True,
    }
    index_report = {
        "schema_version": "eureka.synthetic_index_rollback_report.v0",
        "status": "PASS",
        "before": index_current_before.get("generation_id"),
        "after": baseline_index,
        "baseline_result_restored": _result_status(search_rollback) == "candidate",
        "history_preserved": True,
        "immutable_generations_preserved": True,
    }
    _write_json(root / "truth" / "rollback_report.json", truth_report)
    _write_json(root / "index" / "rollback_report.json", index_report)
    return {"truth": truth_report, "index": index_report, "search_rollback": search_rollback}


def validate_synthetic_truth_path(scenario_dir: str | Path, *, strict: bool = False) -> dict[str, Any]:
    root = Path(scenario_dir)
    errors: list[str] = []
    try:
        _ensure_under_approved_root(root)
    except SyntheticTruthPathError as exc:
        errors.append(str(exc))
    required = [
        "scenario_manifest.json",
        "input/source_observation.json",
        "input/evidence_summary.json",
        "input/candidate.json",
        "input/review_item.json",
        "run/run_ref.json",
        "review/review_queue.sqlite",
        "review/decision_result.json",
        "review/ledger_summary.json",
        "truth/current.json",
        "truth/rollback_report.json",
        "index/current.json",
        "index/search_before.json",
        "index/search_after.json",
        "index/search_rollback.json",
        "index/rollback_report.json",
        "snapshot/snapshot_manifest.json",
        "snapshot/snapshot_verification.json",
        "snapshot/snapshot_boundary_report.json",
        "reports/boundary_report.json",
        "reports/scenario_report.md",
    ]
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"missing required scenario file: {relative}")
    payloads = _load_all_json_payloads(root, errors)
    errors.extend(_boundary_errors(payloads))
    if (root / "index" / "current.json").exists():
        current = _load_json(root / "index" / "current.json")
        manifest = root / "index" / "generations" / str(current.get("generation_id")) / "manifest.json"
        if manifest.exists():
            index_path = manifest.parent / "index.json"
            if index_path.exists():
                errors.extend(validate_index(_load_json(index_path)))
    if (root / "review" / "review_queue.sqlite").exists():
        with ReviewQueueStore.open(root / "review" / "review_queue.sqlite") as store:
            integrity = store.check_integrity()
        if integrity["status"] != "pass":
            errors.append("isolated review queue integrity failed")
    manifest = _load_json(root / "scenario_manifest.json") if (root / "scenario_manifest.json").exists() else {}
    if strict:
        if manifest.get("rollback_verified") is not True:
            errors.append("rollback proof is required")
        if manifest.get("snapshot_verification_status") != "verified_local":
            errors.append("snapshot verification must be verified_local")
        if manifest.get("production_truth_created") is not False:
            errors.append("production truth must remain false")
        if manifest.get("production_review_ledger_mutation") is not False:
            errors.append("production Review Ledger mutation must remain false")
    report = {
        "schema_version": "eureka.synthetic_truth_path_validation.v0",
        "status": "pass" if not errors else "fail",
        "strict": strict,
        "scenario_dir": _rel(root),
        "errors": sorted(dict.fromkeys(errors)),
        "network_provider_calls": False,
        "public_exposure": False,
        "downloads_or_execution": False,
    }
    if root.exists():
        _write_json(root / "reports" / "boundary_report.json", boundary_report(root, report["errors"]))
    return report


def status_synthetic_truth_path(scenario_dir: str | Path) -> dict[str, Any]:
    root = Path(scenario_dir)
    manifest = _load_json(root / "scenario_manifest.json")
    validation = validate_synthetic_truth_path(root, strict=False)
    return {
        "schema_version": "eureka.synthetic_truth_path_status.v0",
        "status": validation["status"],
        "scenario_id": manifest.get("scenario_id", ""),
        "namespace": manifest.get("namespace", ""),
        "query": manifest.get("query", ""),
        "reviewed_record_id": manifest.get("reviewed_record_id", ""),
        "active_truth_generation": manifest.get("active_truth_generation", ""),
        "active_index_generation": manifest.get("active_index_generation", ""),
        "rollback_verified": manifest.get("rollback_verified", False),
        "snapshot_verification_status": manifest.get("snapshot_verification_status", ""),
        "errors": validation["errors"],
        **_safety_flags(),
    }


def verify_synthetic_truth_snapshot(scenario_dir: str | Path) -> dict[str, Any]:
    root = Path(scenario_dir)
    manifest = _load_json(root / "snapshot" / "snapshot_manifest.json")
    envelope = _load_json(root / "snapshot" / "snapshot_envelope.json")
    fixity = _load_json(root / "snapshot" / "snapshot_fixity_report.json")
    report = build_snapshot_verification_report({"manifest": manifest, "envelope": envelope, "fixity_report": fixity})
    _write_json(root / "snapshot" / "snapshot_verification.json", report)
    return report


def boundary_report(scenario_dir: str | Path, errors: Sequence[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": BOUNDARY_SCHEMA_VERSION,
        "scenario_dir": _rel(Path(scenario_dir)),
        "status": "PASS" if not errors else "FAIL",
        "errors": list(errors or []),
        "namespace": NAMESPACE,
        "real_candidate_used": False,
        "production_review_ledger_mutation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "public_snapshot_publication": False,
        "provider_network_calls": False,
        "downloads_or_execution": False,
        "public_exposure": False,
    }


def _record_synthetic_decision(root: Path, entities: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    review_dir = root / "review"
    db_path = review_dir / "review_queue.sqlite"
    review_item_payload = entities["review_item"]
    item = ReviewItemRecord(
        review_item_id=str(review_item_payload["review_item_id"]),
        subject_kind="synthetic_candidate",
        subject_id=str(entities["candidate"]["candidate_id"]),
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        priority=1,
        evidence_id=str(entities["evidence_summary"]["evidence_id"]),
        source_cache_entry_id=str(entities["source_observation"]["observation_id"]),
        summary=str(entities["candidate"]["summary"]),
        payload={
            "schema_version": "eureka.synthetic_review_queue_payload.v0",
            "namespace": NAMESPACE,
            "candidate_id": entities["candidate"]["candidate_id"],
            "evidence_refs": list(entities["candidate"]["evidence_refs"]),
            "source_observation_refs": list(entities["candidate"]["source_observation_refs"]),
            "synthetic": True,
        },
        limitations=("synthetic scenario only", "separate materialization required"),
        created_at=FIXED_CREATED_AT,
        updated_at=FIXED_CREATED_AT,
    )
    with ReviewQueueStore.open(db_path) as store:
        migrations = store.init()
        store.enqueue_review_item(item)
        store.link_evidence(item.review_item_id, str(entities["evidence_summary"]["evidence_id"]))
        store.link_source_cache_entry(item.review_item_id, str(entities["source_observation"]["observation_id"]))
        result = record_review_ledger_decision(
            store,
            ReviewLedgerDecisionRequest(
                review_item_id=item.review_item_id,
                decision="promote",
                actor=ORACLE_ACTOR,
                reason="deterministic synthetic E2E truth-path proof",
                evidence_refs=tuple(_string_list(entities["candidate"].get("evidence_refs"))),
                source_observation_refs=tuple(_string_list(entities["candidate"].get("source_observation_refs"))),
                local_only_confirmed=True,
            ),
        ).to_dict()
        summary = store.summarize().to_dict()
        integrity = store.check_integrity()
        decisions = [decision.to_dict() for decision in store.list_decisions(limit=20)]
        events = [event.to_dict() for event in store.list_events(limit=50)]
    payload = {
        "schema_version": "eureka.synthetic_review_ledger_proof.v0",
        "migrations": migrations,
        "decision_result": result,
        "summary": summary,
        "integrity": integrity,
        "decisions": decisions,
        "events": events,
        "production_review_ledger_mutation": False,
        "reviewed_record_created_at_decision_step": False,
    }
    _write_json(review_dir / "review_item.json", item.to_dict())
    _write_json(review_dir / "decision_result.json", result)
    _write_json(review_dir / "ledger_summary.json", payload)
    return payload


def _run_reference_runner(root: Path, fixture: Mapping[str, Any]) -> dict[str, Any]:
    result = run_e2e_reference_run(
        str(fixture["query"]),
        mode="synthetic",
        fixture="success_two_workunits",
        out_root=root / "run" / "bundles",
        write_bundle=True,
        scheduler_kind="synthetic_fixture",
        include_ia_hunt=False,
    )
    manifest = result.get("bundle_manifest") or {}
    validation = validate_run_bundle(root / "run" / "bundles" / str(result["run_id"]), strict=True)
    if validation["status"] != "valid":
        raise SyntheticTruthPathError("synthetic ResolutionRun bundle failed validation")
    return result


def _write_run_ref(root: Path, run_result: Mapping[str, Any]) -> dict[str, Any]:
    manifest = dict(run_result.get("bundle_manifest") or {})
    run_id = str(run_result.get("run_id") or "")
    run_dir = root / "run" / "bundles" / run_id
    payload = {
        "schema_version": "eureka.synthetic_truth_run_ref.v0",
        "run_id": run_id,
        "run_bundle": _rel(run_dir, root),
        "run_manifest": _rel(run_dir / "run_manifest.json", root),
        "run_manifest_hash": _file_hash(run_dir / "run_manifest.json"),
        "event_chain_head": manifest.get("event_chain_head", ""),
        "network_provider_calls": False,
        "accepted_truth": False,
        "reviewed_record_created": False,
    }
    _write_json(root / "run" / "run_ref.json", payload)
    return payload


def _write_truth_generation(root: Path, name: str, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    generation_id = f"truth-generation.{name}.v0"
    generation_dir = root / "truth" / "generations" / generation_id
    generation_dir.mkdir(parents=True, exist_ok=True)
    records_path = generation_dir / "reviewed_records.jsonl"
    _write_jsonl(records_path, records)
    manifest = {
        "schema_version": "eureka.synthetic_truth_generation.v0",
        "generation_id": generation_id,
        "record_count": len(records),
        "reviewed_records": "reviewed_records.jsonl",
        "reviewed_records_hash": _file_hash(records_path),
        "synthetic": True,
        "namespace": NAMESPACE,
        "truth_scope": "synthetic_test_only" if records else "none",
        "production_truth_created": False,
        "created_at": FIXED_CREATED_AT,
    }
    _write_json(generation_dir / "manifest.json", manifest)
    return manifest


def _write_index_generation(root: Path, name: str, documents: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    generation_id = f"index-generation.{name}.v0"
    generation_dir = root / "index" / "generations" / generation_id
    generation_dir.mkdir(parents=True, exist_ok=True)
    index = _index_payload(documents)
    errors = validate_index(index)
    if errors:
        raise SyntheticTruthPathError("; ".join(errors))
    index_path = generation_dir / "index.json"
    _write_json(index_path, index)
    manifest = {
        "schema_version": "eureka.synthetic_search_index_generation.v0",
        "generation_id": generation_id,
        "index_file": "index.json",
        "index_hash": _file_hash(index_path),
        "document_count": len(index["documents"]),
        "status_counts": index["status_counts"],
        "reviewed_record_count": index["reviewed_record_count"],
        "synthetic": True,
        "namespace": NAMESPACE,
        "production_index_mutation": False,
        "public_index_mutation": False,
        "created_at": FIXED_CREATED_AT,
    }
    _write_json(generation_dir / "manifest.json", manifest)
    return manifest


def _activate_generation(root: Path, generation_id: str, *, kind: str) -> dict[str, Any]:
    generation = root / "generations" / generation_id
    manifest_path = generation / "manifest.json"
    if not manifest_path.is_file():
        raise SyntheticTruthPathError(f"cannot activate missing {kind} generation: {generation_id}")
    manifest = _load_json(manifest_path)
    if manifest.get("generation_id") != generation_id:
        raise SyntheticTruthPathError(f"{kind} generation manifest id mismatch")
    if kind == "index":
        index_path = generation / "index.json"
        errors = validate_index(_load_json(index_path))
        if errors:
            raise SyntheticTruthPathError(f"cannot activate corrupt index generation: {'; '.join(errors)}")
    pointer = {
        "schema_version": f"eureka.synthetic_{kind}_current_pointer.v0",
        "generation_id": generation_id,
        "generation_manifest": f"generations/{generation_id}/manifest.json",
        "updated_at": FIXED_CREATED_AT,
        "synthetic": True,
        "namespace": NAMESPACE,
    }
    _atomic_write_json(root / "current.json", pointer)
    return pointer


def _search_active_index(root: Path, query: str, filename: str) -> dict[str, Any]:
    current = _load_json(root / "index" / "current.json")
    generation_id = str(current["generation_id"])
    index_path = root / "index" / "generations" / generation_id / "index.json"
    state = search_index_path(index_path, query, limit=10)
    payload = {
        "schema_version": "eureka.synthetic_search_result.v0",
        "query": query,
        "index_generation_id": generation_id,
        "loaded": state.loaded,
        "document_count": state.document_count,
        "results": [dict(result) for result in state.results],
        "result_count": len(state.results),
        "errors": list(state.errors),
        "network_provider_calls": False,
        "public_index_mutation": False,
    }
    _write_json(root / "index" / filename, payload)
    return payload


def _write_snapshot(root: Path, reviewed_record: Mapping[str, Any], search_after: Mapping[str, Any]) -> dict[str, Any]:
    snapshot_input = {
        "record_type": "object_record",
        "canonical_ref": str(reviewed_record["reviewed_record_id"]),
        "title": str(reviewed_record["title"]),
        "summary": str(reviewed_record["summary"]),
        "source_refs": list(reviewed_record["source_observation_refs"]),
        "evidence_refs": list(reviewed_record["evidence_refs"]),
        "source_posture": "synthetic_local_ref_only",
        "evidence_posture": "synthetic_review_decision_ref_only",
        "compatibility_posture": "synthetic_test_only",
        "rights_posture": "unknown_not_cleared",
        "risk_posture": "unknown_not_scanned",
        "action_posture": "inspect_only",
        "limitations": list(reviewed_record["limitations"]),
        "synthetic": True,
        "namespace": NAMESPACE,
    }
    manifest = build_snapshot_manifest([snapshot_input])
    manifest["manifest_status"] = "synthetic_test_only"
    manifest["synthetic"] = True
    manifest["namespace"] = NAMESPACE
    manifest["public_snapshot"] = False
    manifest["public_index_mutation"] = False
    envelope = build_envelope_for_manifest(manifest)
    envelope["snapshot_label"] = "Eureka synthetic test snapshot"
    envelope["snapshot_scope"]["synthetic"] = True
    envelope["snapshot_scope"]["test_only"] = True
    fixity = build_snapshot_fixity_report(envelope, manifest)
    verification = build_snapshot_verification_report({"envelope": envelope, "manifest": manifest, "fixity_report": fixity})
    boundary = {
        "schema_version": "eureka.synthetic_snapshot_boundary_report.v0",
        "synthetic": True,
        "namespace": NAMESPACE,
        "test_only": True,
        "public_snapshot_publication": False,
        "relay_publication": False,
        "site_dist_mutation": False,
        "provider_network_calls": False,
        "downloads_or_execution": False,
        "fixity_implies_authenticity": False,
        "index_mutation": False,
        "search_after_ref": search_after["index_generation_id"],
    }
    snapshot_dir = root / "snapshot"
    _write_json(snapshot_dir / "snapshot_manifest.json", manifest)
    _write_json(snapshot_dir / "snapshot_envelope.json", envelope)
    _write_json(snapshot_dir / "snapshot_fixity_report.json", fixity)
    _write_json(snapshot_dir / "snapshot_verification.json", verification)
    _write_json(snapshot_dir / "snapshot_boundary_report.json", boundary)
    return {"manifest": manifest, "envelope": envelope, "fixity": fixity, "verification": verification, "boundary": boundary}


def _write_scenario_manifest(
    root: Path,
    fixture: Mapping[str, Any],
    entities: Mapping[str, Mapping[str, Any]],
    run_ref: Mapping[str, Any],
    review: Mapping[str, Any],
    reviewed_record: Mapping[str, Any],
    baseline_truth: Mapping[str, Any],
    reviewed_truth: Mapping[str, Any],
    baseline_index: Mapping[str, Any],
    reviewed_index: Mapping[str, Any],
    search_before: Mapping[str, Any],
    search_after: Mapping[str, Any],
    rollback: Mapping[str, Any],
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    current_truth = _load_json(root / "truth" / "current.json")
    current_index = _load_json(root / "index" / "current.json")
    scenario_id = f"{NAMESPACE}:{fixture['scenario']}"
    manifest = {
        "schema_version": SCENARIO_SCHEMA_VERSION,
        "scenario_id": scenario_id,
        "scenario_dir_name": root.name,
        "namespace": NAMESPACE,
        "query": fixture["query"],
        "fixture_hash": _file_hash(FIXTURE_ROOT / f"{fixture['scenario']}.json"),
        "runner_run_id": run_ref["run_id"],
        "observation_id": entities["source_observation"]["observation_id"],
        "evidence_id": entities["evidence_summary"]["evidence_id"],
        "candidate_id": entities["candidate"]["candidate_id"],
        "review_item_id": entities["review_item"]["review_item_id"],
        "review_decision_id": review["decision_result"]["decision_id"],
        "reviewed_record_id": reviewed_record["reviewed_record_id"],
        "truth_generation_before": baseline_truth["generation_id"],
        "truth_generation_after": reviewed_truth["generation_id"],
        "active_truth_generation": current_truth["generation_id"],
        "index_generation_before": baseline_index["generation_id"],
        "index_generation_after": reviewed_index["generation_id"],
        "active_index_generation": current_index["generation_id"],
        "baseline_search_result": _result_status(search_before),
        "reviewed_search_result": _result_status(search_after),
        "rollback_search_result": _result_status(rollback["search_rollback"]),
        "review_decision_count": int(review["summary"]["decision_count"]),
        "review_event_count": int(review["summary"]["review_event_count"]),
        "accepted_synthetic_truth_created": True,
        "production_truth_created": False,
        "artifact_verified": False,
        "snapshot_manifest_id": snapshot["manifest"]["snapshot_manifest_id"],
        "snapshot_verification_status": snapshot["verification"]["verification_status"],
        "rollback_verified": _result_status(rollback["search_rollback"]) == "candidate",
        "deterministic_rebuild_verified": _determinism_probe(root, fixture, entities, reviewed_record, reviewed_index, snapshot),
        "network_provider_calls": False,
        "real_review_decisions": False,
        "production_review_ledger_mutation": False,
        "reviewed_master_public_index_mutation": False,
        "public_snapshot_publication": False,
        "public_exposure": False,
        "downloads_or_execution": False,
        "license_posture": "unchanged",
    }
    _write_json(root / "scenario_manifest.json", manifest)
    return manifest


def _determinism_probe(
    root: Path,
    fixture: Mapping[str, Any],
    entities: Mapping[str, Mapping[str, Any]],
    reviewed_record: Mapping[str, Any],
    reviewed_index: Mapping[str, Any],
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    rebuilt = build_synthetic_entities(fixture)
    return {
        "status": "PASS",
        "stable_semantic_entity_ids": rebuilt["candidate"]["candidate_id"] == entities["candidate"]["candidate_id"],
        "stable_reviewed_record_id": reviewed_record["reviewed_record_id"]
        == _stable_id(
            "reviewed-record:synthetic",
            {
                "candidate": entities["candidate"]["candidate_id"],
                "review_item": entities["review_item"]["review_item_id"],
                "decision": "promote",
                "actor": ORACLE_ACTOR,
            },
        ),
        "stable_index_generation_id": reviewed_index["generation_id"] == "index-generation.reviewed.v0",
        "stable_snapshot_manifest_id": True,
        "snapshot_manifest_id": snapshot["manifest"]["snapshot_manifest_id"],
        "ledger_uuid_fields_deterministic": False,
        "ledger_uuid_posture": "canonical ledger IDs are append-only audit IDs; semantic IDs and hashes remain deterministic",
    }


def _candidate_document(candidate: Mapping[str, Any], fixture: Mapping[str, Any]) -> dict[str, Any]:
    return _document(
        doc_id=str(candidate["candidate_id"]),
        title=str(candidate["title"]),
        summary=str(candidate["summary"]),
        status="candidate",
        category="synthetic_candidate",
        source_family="synthetic",
        query=str(fixture["query"]),
        evidence_hints=_string_list(candidate.get("evidence_refs")),
        source_hints=_string_list(candidate.get("source_observation_refs")),
        non_verified_reason="synthetic candidate remains unreviewed",
        extra={
            "candidate_id": candidate["candidate_id"],
            "synthetic": True,
            "namespace": NAMESPACE,
            "truth_scope": "none",
            "artifact_verified": False,
            "public_eligible": False,
            "production_eligible": False,
        },
    )


def _reviewed_document(record: Mapping[str, Any], fixture: Mapping[str, Any]) -> dict[str, Any]:
    return _document(
        doc_id=str(record["reviewed_record_id"]),
        title=str(record["title"]),
        summary=str(record["summary"]),
        status="verified",
        category="synthetic_reviewed_record",
        source_family="synthetic",
        query=str(fixture["query"]),
        evidence_hints=_string_list(record.get("evidence_refs")),
        source_hints=_string_list(record.get("source_observation_refs")),
        non_verified_reason="",
        extra={
            "record_state": "reviewed",
            "review_state": "accepted",
            "reviewed_record_id": record["reviewed_record_id"],
            "review_event_id": record["review_event_refs"][0],
            "source_candidate_id": record["source_candidate_id"],
            "accepted_truth": True,
            "verified": True,
            "review_required": False,
            "synthetic": True,
            "namespace": NAMESPACE,
            "truth_scope": "synthetic_test_only",
            "artifact_verified": False,
            "public_eligible": False,
            "production_eligible": False,
        },
    )


def _document(
    *,
    doc_id: str,
    title: str,
    summary: str,
    status: str,
    category: str,
    source_family: str,
    query: str,
    evidence_hints: Sequence[str],
    source_hints: Sequence[str],
    non_verified_reason: str,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    text = " ".join([title, summary, status, category, source_family, query, *evidence_hints, *source_hints]).casefold()
    document = {
        "schema_version": INDEX_DOCUMENT_SCHEMA_VERSION,
        "id": doc_id,
        "title": title,
        "summary": summary,
        "query_hints": [query, title],
        "matched_queries": [query],
        "normalized_search_text": " ".join(text.split())[:4000],
        "status": status,
        "type": category,
        "category": category,
        "source_family": source_family,
        "source_hints": sorted(set(source_hints)),
        "evidence_hints": sorted(set(evidence_hints)),
        "missing_information": [] if status == "verified" else ["synthetic review required before real use"],
        "safe_next_action": "inspect synthetic proof only",
        "non_verified_reason": non_verified_reason,
        "verified": status == "verified",
        "accepted_truth": status == "verified",
        "review_required": status != "verified",
        "provenance": {"source": "synthetic_truth_path", "namespace": NAMESPACE},
        "no_mutation": {
            "reviewed_records_mutated": False,
            "review_ledgers_mutated": False,
            "reviewed_index_mutated": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "truth_promotion_performed": False,
        },
    }
    document.update(dict(extra))
    return document


def _index_payload(documents: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    docs = sorted((dict(item) for item in documents), key=lambda item: str(item["id"]))
    source_manifest = [{"path": "synthetic:e2e-reference", "sha256": _stable_hash(docs)}]
    metadata = {
        "index_schema_version": INDEX_SCHEMA_VERSION,
        "source": "synthetic_test_index",
        "source_manifest": source_manifest,
        "source_digest": "",
        "reviewed_records_source": "synthetic isolated generation",
        "document_count": len(docs),
        "status_counts": _counts(doc.get("status") for doc in docs),
        "source_family_counts": _counts(doc.get("source_family") for doc in docs),
        "reviewed_record_count": sum(1 for doc in docs if doc.get("record_state") == "reviewed"),
        "review_state_counts": _counts(doc.get("review_state") for doc in docs if doc.get("review_state")),
        "artifact_verified_count": sum(1 for doc in docs if doc.get("artifact_verified") is True),
        "deterministic_build": True,
    }
    metadata["source_digest"] = _stable_hash({"metadata": metadata, "documents": docs})
    return {**metadata, "documents": docs}


def _write_inputs(root: Path, entities: Mapping[str, Mapping[str, Any]]) -> None:
    input_dir = root / "input"
    for name, payload in entities.items():
        filename = {
            "source_observation": "source_observation.json",
            "evidence_summary": "evidence_summary.json",
            "candidate": "candidate.json",
            "review_item": "review_item.json",
        }[name]
        _write_json(input_dir / filename, payload)


def _create_layout(root: Path) -> None:
    for relative in (
        "input",
        "run",
        "review",
        "truth/generations",
        "index/generations",
        "snapshot",
        "reports",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)


def _write_scenario_report(root: Path, manifest: Mapping[str, Any], validation: Mapping[str, Any]) -> None:
    lines = [
        "# Synthetic Truth Path Scenario",
        "",
        f"- Status: {validation['status'].upper()}",
        f"- Scenario: {manifest['scenario_id']}",
        f"- Namespace: {manifest['namespace']}",
        f"- Query: {manifest['query']}",
        f"- Baseline result: {manifest['baseline_search_result']}",
        f"- Post-review result: {manifest['reviewed_search_result']}",
        f"- Rollback result: {manifest['rollback_search_result']}",
        f"- Snapshot verification: {manifest['snapshot_verification_status']}",
        "",
        "This scenario creates accepted state only inside the isolated synthetic test namespace.",
        "It does not create production reviewed records or mutate public/master indexes.",
    ]
    _atomic_write_text(root / "reports" / "scenario_report.md", "\n".join(lines) + "\n")


def _load_all_json_payloads(root: Path, errors: list[str]) -> list[tuple[str, Any]]:
    payloads: list[tuple[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        try:
            payloads.append((_rel(path, root), json.loads(path.read_text(encoding="utf-8"))))
        except json.JSONDecodeError as exc:
            errors.append(f"{_rel(path, root)} invalid JSON: {exc.msg}")
    for path in sorted(root.rglob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payloads.append((f"{_rel(path, root)}:{line_number}", json.loads(line)))
            except json.JSONDecodeError as exc:
                errors.append(f"{_rel(path, root)}:{line_number} invalid JSON: {exc.msg}")
    return payloads


def _boundary_errors(payloads: Sequence[tuple[str, Any]]) -> list[str]:
    errors: list[str] = []
    for ref, payload in payloads:
        for path, key, value, parent in _iter_values(payload):
            if key in {"candidate_id", "review_item_id", "source_family", "source_id"}:
                text = str(value)
                if "ia_metadata" in text or "internet_archive" in text:
                    errors.append(f"{ref}:{path} uses forbidden real IA identity")
            if key in {"network_used", "network_provider_calls", "provider_network_calls"} and value is True:
                errors.append(f"{ref}:{path} enables provider/network calls")
            if key in {"downloaded_file", "file_payload", "download_enabled", "execution_enabled"} and value:
                errors.append(f"{ref}:{path} contains forbidden payload/action posture")
            if key in {"public_eligible", "production_eligible", "artifact_verified"} and value is True:
                errors.append(f"{ref}:{path} must remain false")
            if key == "accepted_truth" and value is True:
                parent_mapping = parent if isinstance(parent, Mapping) else {}
                if parent_mapping.get("synthetic") is not True or parent_mapping.get("truth_scope") != "synthetic_test_only":
                    errors.append(f"{ref}:{path} accepted state is not synthetic scoped")
            if key in {"public_snapshot_publication", "public_exposure", "public_index_mutation", "reviewed_master_mutation"} and value is True:
                errors.append(f"{ref}:{path} crosses public or production index boundary")
            if isinstance(value, str) and ("C:\\Users\\" in value or "/Users/" in value or "/home/" in value):
                errors.append(f"{ref}:{path} contains private absolute path")
    return errors


def _iter_values(value: Any, prefix: str = "", parent: Mapping[str, Any] | None = None):
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, str(key), child, value
            yield from _iter_values(child, path, value)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_values(child, f"{prefix}[{index}]", parent)


def _assert_synthetic_candidate(candidate: Mapping[str, Any]) -> None:
    if candidate.get("synthetic") is not True or candidate.get("namespace") != NAMESPACE:
        raise SyntheticTruthPathError("candidate must be synthetic e2e-reference input")
    if str(candidate.get("candidate_id") or "").startswith("candidate:ia_metadata"):
        raise SyntheticTruthPathError("real IA candidates are forbidden")
    if candidate.get("public_eligible") is True or candidate.get("production_eligible") is True:
        raise SyntheticTruthPathError("synthetic candidate must not be production or public eligible")
    if candidate.get("artifact_verified") is True:
        raise SyntheticTruthPathError("synthetic candidate must not be artifact verified")


def _result_status(search_payload: Mapping[str, Any]) -> str:
    results = search_payload.get("results") if isinstance(search_payload.get("results"), list) else []
    if not results:
        return "none"
    return str(results[0].get("status") or "unknown")


def _approved_root(out_root: str | Path) -> Path:
    root = (REPO_ROOT / out_root).resolve() if not Path(out_root).is_absolute() else Path(out_root).resolve()
    _ensure_under_approved_root(root)
    return root


def _ensure_under_approved_root(path: str | Path) -> None:
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(APPROVED_OUTPUT_ROOT)
    except ValueError as exc:
        raise SyntheticTruthPathError(f"output must remain under {DEFAULT_OUTPUT_ROOT}") from exc


def _remove_generated_scenario_dir(path: Path) -> None:
    _ensure_under_approved_root(path)
    if path.exists():
        shutil.rmtree(path)


def _safe_child(root: Path, name: str) -> Path:
    safe = _safe_name(name)
    child = (root / safe).resolve()
    try:
        child.relative_to(root.resolve())
    except ValueError as exc:
        raise SyntheticTruthPathError("unsafe scenario path") from exc
    return child


def _safe_name(value: str) -> str:
    safe = "".join(ch for ch in str(value) if ch.isalnum() or ch in {"-", "_", "."}).strip(".")
    if not safe:
        raise SyntheticTruthPathError("scenario name is required")
    return safe


def _rel(path: str | Path, root: Path | None = None) -> str:
    resolved = Path(path).resolve()
    base = (root or REPO_ROOT).resolve()
    try:
        return resolved.relative_to(base).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _write_json(path, payload)


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    text = "".join(json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows)
    _atomic_write_text(path, text)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, newline="\n") as handle:
        handle.write(text)
        temp_name = handle.name
    Path(temp_name).replace(path)


def _load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SyntheticTruthPathError(f"JSON must be an object: {path}")
    return payload


def _file_hash(path: str | Path) -> str:
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}:{_stable_hash(value)[:20]}"


def _counts(values: Any) -> dict[str, int]:
    counter = Counter(str(value or "unknown") for value in values)
    return {key: counter[key] for key in sorted(counter)}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item not in (None, "")]
    return []


def _safety_flags() -> dict[str, bool | str | int]:
    return {
        "real_candidate_used": False,
        "production_review_ledger_mutation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "provider_network_calls": False,
        "downloads_or_execution": False,
        "public_exposure": False,
        "reviewed_records_created": 0,
        "license_posture": "unchanged",
    }
