"""Fixture-only source observation vertical slice.

This module composes existing local runtime stores into one deterministic
source -> evidence -> review -> index -> search/absence loop. It does not
call live sources, connectors, providers, or hosted services.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Mapping

from runtime.evidence_ledger import EvidenceCandidateRecord, EvidenceLedgerStore, EvidenceReviewStatus
from runtime.public_index import PublicIndexStore, rebuild_reviewed_public_index
from runtime.review_queue import ReviewDecision, ReviewDecisionKind, ReviewItemRecord, ReviewQueueStore
from runtime.source_cache import SourceCacheStatus, SourceCacheStore, build_cache_entry
from runtime.source_observation import (
    MetadataRequest,
    MetadataResponse,
    SourceCapability,
    SourceId,
    SourceLocator,
    SourcePolicy,
    SourceRecord,
    build_evidence_candidate,
    build_source_observation,
    normalize_metadata_response,
)


SCHEMA_VERSION = "eureka.fixture_source_observation_slice.v0"
SURFACE_SCHEMA_VERSION = "eureka.fixture_object_absence_surface.v0"
REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION = "eureka.fixture_reviewed_index_artifact.v0"
REVIEWED_INDEX_ARTIFACT_ID = "ria_fixture_demo_project_v0"
REVIEWED_INDEX_BUILDER_ID = "eureka.fixture_reviewed_index_persistence.v0"
FIXTURE_TIMESTAMP = "2026-05-12T00:00:00Z"
FIXTURE_RESPONSE_TIMESTAMP = "2026-05-12T00:00:01Z"
POSITIVE_QUERY = "demo project"
ABSENCE_QUERY = "zzznomatch"
RESULT_PACKET_ID = "srp_fixture_demo_project_v0"
OBJECT_DETAIL_PACKET_ID = "odp_fixture_demo_project_v0"
EVIDENCE_SUMMARY_PACKET_ID = "esp_fixture_demo_project_v0"
SOURCE_PROVENANCE_PACKET_ID = "spp_fixture_local_metadata_v0"
ABSENCE_PACKET_ID = "ap_fixture_zzznomatch_v0"

FORBIDDEN_OUTPUT_ROOTS = {
    ".aide.local",
    ".cache",
    ".env",
    ".git",
    ".github",
    ".local",
    "contracts",
    "crates",
    "evals",
    "examples",
    "native",
    "runtime",
    "scripts",
    "secrets",
    "site",
    "snapshots",
    "surfaces",
    "tests",
}


def run_fixture_source_observation_slice(output_root: str | Path | None = None) -> dict[str, Any]:
    """Run one local fixture-only source/evidence/review/index loop."""

    root = resolve_output_root(output_root)
    root.mkdir(parents=True, exist_ok=True)

    paths = {
        "source_cache": root / "source-cache.sqlite",
        "evidence_ledger": root / "evidence-ledger.sqlite",
        "review_queue": root / "review-queue.sqlite",
        "public_index": root / "public-index.sqlite",
        "reviewed_index_artifact": root / "reviewed-index-artifact.json",
    }
    for path in paths.values():
        path.unlink(missing_ok=True)

    source_record, request, response = build_fixture_source_material()
    normalized = normalize_metadata_response(response, source_record, policy=_fixture_policy())
    observation = build_source_observation(
        response,
        source_record,
        policy=_fixture_policy(),
        observed_fields=normalized.normalized_fields,
    )
    evidence_candidate = build_evidence_candidate(normalized)

    with SourceCacheStore.open(paths["source_cache"]) as cache_store:
        cache_store.init()
        cache_store.write_source_record(source_record)
        cache_store.write_metadata_response(response)
        cache_store.write_source_observation(observation)
        cache_store.write_normalized_observation(normalized)
        cache_entry = build_cache_entry(
            source_record,
            response,
            observation,
            normalized,
            status=SourceCacheStatus.CACHED,
        )
        cache_store.write_cache_entry(cache_entry)
        source_cache_summary = cache_store.summarize()
        source_cache_integrity = cache_store.check_integrity()

    evidence_record = EvidenceCandidateRecord.from_candidate(
        evidence_candidate,
        normalized_observation_id=normalized.normalized_observation_id,
        source_cache_entry_id=cache_entry.entry_id,
        status=EvidenceReviewStatus.CANDIDATE,
    )
    with EvidenceLedgerStore.open(paths["evidence_ledger"]) as ledger:
        ledger.init()
        ledger.write_evidence_candidate(evidence_record)
        ledger.link_source_cache_entry(evidence_record.evidence_id, cache_entry.entry_id)
        ledger.set_review_status(
            evidence_record.evidence_id,
            EvidenceReviewStatus.NEEDS_REVIEW,
            reason="fixture evidence candidate requires local review before index projection",
        )
        stored_evidence = ledger.get_evidence_candidate(evidence_record.evidence_id) or evidence_record
        evidence_summary = ledger.summarize()
        evidence_integrity = ledger.check_integrity()

    review_item = ReviewItemRecord.from_evidence(stored_evidence, source_cache_entry_id=cache_entry.entry_id)
    review_decision = ReviewDecision(
        review_item_id=review_item.review_item_id,
        decision_kind=ReviewDecisionKind.ACCEPT,
        decision_actor="operator:fixture-q58",
        decision_id="rvd_fixture_demo_project_accept_v0",
        reason="local fixture accepted for isolated reviewed-index candidate only",
        payload={"local_fixture_only": True, "q58_scope": "isolated_vertical_slice"},
        limitations=("local fixture decision only", "not a production or hosted review"),
        created_at=FIXTURE_RESPONSE_TIMESTAMP,
    )
    with ReviewQueueStore.open(paths["review_queue"]) as queue:
        queue.init()
        queue.enqueue_review_item(review_item)
        queue.link_evidence(review_item.review_item_id, stored_evidence.evidence_id)
        queue.link_source_cache_entry(review_item.review_item_id, cache_entry.entry_id)
        queue.record_decision(review_item.review_item_id, review_decision)
        stored_review_item = queue.get_review_item(review_item.review_item_id) or review_item
        stored_decisions = queue.list_decisions(review_item.review_item_id)
        stored_review_decision = stored_decisions[-1] if stored_decisions else review_decision
        review_summary = queue.summarize()
        review_integrity = queue.check_integrity()

    rebuild_report = rebuild_reviewed_public_index(
        paths["source_cache"],
        paths["evidence_ledger"],
        paths["review_queue"],
        paths["public_index"],
        dry_run=False,
    )
    with PublicIndexStore.open(paths["public_index"]) as index_store:
        index_store.init()
        public_records = index_store.list_records()
        search_results = index_store.search(POSITIVE_QUERY, limit=10)
        absence_report = index_store.absence_report(ABSENCE_QUERY)
        public_index_summary = index_store.summarize()
        public_index_integrity = index_store.check_integrity()

    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "fixture": build_fixture_payload(),
        "paths": {key: str(path) for key, path in paths.items()},
        "source_record": source_record.to_dict(),
        "metadata_request": request.to_dict(),
        "metadata_response": response.to_dict(),
        "source_observation": observation.to_dict(),
        "normalized_observation": normalized.to_dict(),
        "source_cache_entry": cache_entry.to_dict(),
        "evidence_candidate": evidence_candidate.to_dict(),
        "evidence_record": stored_evidence.to_dict(),
        "review_item": stored_review_item.to_dict(),
        "review_decision": stored_review_decision.to_dict(),
        "rebuild_report": rebuild_report,
        "reviewed_index_candidate": public_records[0].to_dict() if public_records else {},
        "public_index_records": [record.to_dict() for record in public_records],
        "search": {
            "query": POSITIVE_QUERY,
            "result_count": len(search_results),
            "results": [result.to_dict() for result in search_results],
        },
        "object_result": public_records[0].to_dict() if public_records else {},
        "absence": absence_report.to_dict(),
        "summaries": {
            "source_cache": source_cache_summary.to_dict(),
            "evidence_ledger": evidence_summary.to_dict(),
            "review_queue": review_summary.to_dict(),
            "public_index": public_index_summary.to_dict(),
        },
        "integrity": {
            "source_cache": source_cache_integrity,
            "evidence_ledger": evidence_integrity,
            "review_queue": review_integrity,
            "public_index": public_index_integrity,
        },
        "no_live_no_mutation": no_live_no_mutation_claims(root),
    }
    report["surface_packets"] = build_inspection_surface_packets(report)
    artifact = build_reviewed_index_artifact(report)
    artifact_path = paths["reviewed_index_artifact"]
    write_reviewed_index_artifact(artifact_path, artifact)
    loaded_artifact = load_reviewed_index_artifact(artifact_path)
    report["persistent_reviewed_index"] = {
        "schema_version": REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION,
        "artifact_path": str(artifact_path),
        "artifact_id": loaded_artifact.get("artifact_id"),
        "artifact_hash": loaded_artifact.get("artifact_hash"),
        "artifact_file_sha256": _file_sha256(artifact_path),
        "record_count": len(loaded_artifact.get("records", []) or []),
        "indexed_object_ids": [str(record.get("record_id")) for record in loaded_artifact.get("records", []) or []],
        "local_only": loaded_artifact.get("local_only"),
        "fixture_only": loaded_artifact.get("fixture_only"),
        "production_public_index": loaded_artifact.get("production_public_index"),
        "artifact": loaded_artifact,
        "validation_errors": validate_reviewed_index_artifact(loaded_artifact),
        "search_from_artifact": search_reviewed_index_artifact(loaded_artifact, POSITIVE_QUERY),
        "object_from_artifact": get_reviewed_index_artifact_object(
            loaded_artifact,
            str(report.get("object_result", {}).get("record_id", "")),
        ),
        "absence_from_artifact": absence_from_reviewed_index_artifact(loaded_artifact, ABSENCE_QUERY),
    }
    errors = validate_fixture_slice_report(report)
    if errors:
        report["status"] = "fail"
        report["errors"] = errors
    return report


def build_fixture_source_material() -> tuple[SourceRecord, MetadataRequest, MetadataResponse]:
    source_record = SourceRecord(
        source_id=SourceId("source.fixture.local.metadata"),
        source_family="local_fixture",
        trust_lane="synthetic_fixture",
        label="Q58 synthetic package metadata source",
        locators=(
            SourceLocator(
                kind="local_fixture",
                value="fixture://q58/demo-project",
                label="demo-project",
                metadata={"fixture_only": True},
            ),
        ),
        capabilities=(
            SourceCapability(
                name="metadata_observation",
                operations=("metadata_observation",),
                limitations=("fixture payload only", "no live request"),
            ),
        ),
        limitations=("fixture payload only", "no live request", "isolated local stores only"),
        metadata={"task": "Q58", "fixture": "demo-project"},
    )
    request = MetadataRequest.build(
        source_id=source_record.source_id,
        request_kind="fixture_package_metadata",
        target="demo-project",
        parameters={"name": "demo-project", "mode": "fixture_local_only"},
        created_at=FIXTURE_TIMESTAMP,
    )
    response = MetadataResponse.build(
        request_id=request.request_id,
        source_id=source_record.source_id,
        status="observed",
        payload=build_fixture_payload(),
        observed_at=FIXTURE_RESPONSE_TIMESTAMP,
        limitations=("fixture payload only", "no network request performed"),
    )
    return source_record, request, response


def build_fixture_payload() -> dict[str, Any]:
    return {
        "artifact_id": "fixture.demo-project",
        "name": "demo-project",
        "title": "Demo Project",
        "version": "1.0.0",
        "summary": "Synthetic local metadata used by the Q58 fixture vertical slice",
        "source_reference": "fixture://q58/demo-project",
        "provenance": {
            "kind": "repo_local_fixture",
            "observed_at": FIXTURE_RESPONSE_TIMESTAMP,
            "external_call_performed": False,
        },
        "quality_flags": {
            "fixture_only": True,
            "requires_local_review": True,
        },
    }


def validate_fixture_slice_report(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    required = {
        "source_observation",
        "normalized_observation",
        "source_cache_entry",
        "evidence_candidate",
        "evidence_record",
        "review_item",
        "review_decision",
        "reviewed_index_candidate",
        "search",
        "object_result",
        "absence",
        "no_live_no_mutation",
        "surface_packets",
        "persistent_reviewed_index",
    }
    missing = sorted(required - set(report))
    if missing:
        errors.append("missing required report fields: " + ", ".join(missing))
    search = report.get("search", {})
    if not isinstance(search, Mapping) or search.get("query") != POSITIVE_QUERY:
        errors.append("positive search query is missing")
    elif int(search.get("result_count", 0) or 0) < 1:
        errors.append("positive search returned no reviewed result")
    elif not search.get("results"):
        errors.append("positive search result packet is missing")
    absence = report.get("absence", {})
    if not isinstance(absence, Mapping) or absence.get("query") != ABSENCE_QUERY:
        errors.append("absence query is missing")
    elif int(absence.get("result_count", -1) or 0) != 0:
        errors.append("absence query should have zero results")
    review_decision = report.get("review_decision", {})
    if not isinstance(review_decision, Mapping) or review_decision.get("decision_status") != "accepted":
        errors.append("review decision was not accepted")
    index_records = report.get("public_index_records", [])
    if not isinstance(index_records, list) or len(index_records) != 1:
        errors.append("expected exactly one reviewed local index candidate")
    object_result = report.get("object_result", {})
    if not isinstance(object_result, Mapping) or not object_result.get("record_id"):
        errors.append("object result packet is missing record identity")
    elif object_result.get("evidence_id") != report.get("evidence_record", {}).get("evidence_id"):
        errors.append("object result evidence ref does not match evidence record")
    rebuild_report = report.get("rebuild_report", {})
    if isinstance(rebuild_report, Mapping):
        if rebuild_report.get("input_stores_mutated") is not False:
            errors.append("rebuild report must prove input stores were not mutated")
        if rebuild_report.get("master_index_mutated") is not False:
            errors.append("rebuild report must prove master index was not mutated")
        if rebuild_report.get("site_dist_mutated") is not False:
            errors.append("rebuild report must prove site dist was not mutated")
    else:
        errors.append("rebuild report is missing")
    proof = report.get("no_live_no_mutation", {})
    if not isinstance(proof, Mapping):
        errors.append("no-live/no-mutation proof is missing")
    else:
        for key, expected in _required_no_live_flags().items():
            if proof.get(key) is not expected:
                errors.append(f"no_live_no_mutation.{key} must be {expected}")
    surface_packets = report.get("surface_packets", {})
    if not isinstance(surface_packets, Mapping):
        errors.append("surface packets are missing")
    else:
        errors.extend(validate_inspection_surface_packets(surface_packets, report))
    persistent = report.get("persistent_reviewed_index", {})
    if not isinstance(persistent, Mapping):
        errors.append("persistent reviewed index artifact proof is missing")
    else:
        if persistent.get("schema_version") != REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION:
            errors.append(f"persistent reviewed index schema_version must be {REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION}")
        if persistent.get("local_only") is not True or persistent.get("fixture_only") is not True:
            errors.append("persistent reviewed index must be local_only and fixture_only")
        if persistent.get("production_public_index") is not False:
            errors.append("persistent reviewed index must not be a production public index")
        if int(persistent.get("record_count", 0) or 0) != 1:
            errors.append("persistent reviewed index must contain one accepted fixture record")
        if persistent.get("validation_errors") not in ([], ()):
            errors.append("persistent reviewed index validation errors must be empty")
        search_from_artifact = _mapping_at(persistent, "search_from_artifact")
        if search_from_artifact.get("query") != POSITIVE_QUERY or int(search_from_artifact.get("result_count", 0) or 0) != 1:
            errors.append("persistent reviewed index search must return the positive fixture result")
        object_from_artifact = _mapping_at(persistent, "object_from_artifact")
        if object_from_artifact.get("found") is not True:
            errors.append("persistent reviewed index object lookup must find the fixture object")
        absence_from_artifact = _mapping_at(persistent, "absence_from_artifact")
        if absence_from_artifact.get("query") != ABSENCE_QUERY or int(absence_from_artifact.get("result_count", -1) or 0) != 0:
            errors.append("persistent reviewed index absence query must return zero results")
    return errors


def build_inspection_surface_packets(report: Mapping[str, Any]) -> dict[str, Any]:
    """Build stable result/object/evidence/source/absence packets for inspection."""

    normalized_fields = _mapping_at(report, "normalized_observation", "normalized_fields")
    object_result = _mapping_at(report, "object_result")
    evidence_record = _mapping_at(report, "evidence_record")
    evidence_candidate = _mapping_at(report, "evidence_candidate")
    review_decision = _mapping_at(report, "review_decision")
    source_record = _mapping_at(report, "source_record")
    source_observation = _mapping_at(report, "source_observation")
    normalized_observation = _mapping_at(report, "normalized_observation")
    source_cache_entry = _mapping_at(report, "source_cache_entry")
    absence = _mapping_at(report, "absence")
    proof = _mapping_at(report, "no_live_no_mutation")
    search = _mapping_at(report, "search")
    search_results = search.get("results", [])
    first_search_result = search_results[0] if search_results else {}

    artifact_id = str(normalized_fields.get("artifact_id") or object_result.get("record_id") or "")
    title = str(object_result.get("title") or normalized_fields.get("title") or "")
    version = str(normalized_fields.get("version") or "")
    source_id = str(source_record.get("id") or evidence_record.get("source_id") or "")
    source_reference = str(normalized_fields.get("source_reference") or "")
    evidence_id = str(evidence_record.get("evidence_id") or "")
    review_decision_id = str(review_decision.get("decision_id") or "")
    review_status = str(review_decision.get("decision_status") or "")
    record_id = str(object_result.get("record_id") or first_search_result.get("record_id") or "")

    result_packet = {
        "schema_version": "eureka.search_result_packet.v0",
        "packet_id": RESULT_PACKET_ID,
        "query": POSITIVE_QUERY,
        "result_count": int(search.get("result_count", 0) or 0),
        "local_only": True,
        "fixture_only": True,
        "results": [
            {
                "result_id": record_id,
                "object_id": record_id,
                "artifact_id": artifact_id,
                "title": title,
                "version": version,
                "source_id": source_id,
                "source_reference": source_reference,
                "evidence_summary_id": EVIDENCE_SUMMARY_PACKET_ID,
                "evidence_id": evidence_id,
                "review_status": review_status,
                "review_decision_id": review_decision_id,
                "confidence": evidence_candidate.get("confidence"),
                "matched_terms": list(first_search_result.get("matched_terms", []) or []),
                "warnings": _unique_strings(first_search_result.get("warnings", [])),
                "actions": ("inspect_object", "inspect_evidence", "inspect_source", "inspect_absence_scope"),
                "local_only": True,
                "fixture_only": True,
            }
        ],
    }

    object_detail_packet = {
        "schema_version": "eureka.object_detail_packet.v0",
        "packet_id": OBJECT_DETAIL_PACKET_ID,
        "object_id": record_id,
        "identity": {
            "artifact_id": artifact_id,
            "name": str(normalized_fields.get("name") or ""),
            "source_id": source_id,
        },
        "display": {
            "title": title,
            "version": version,
            "description": str(object_result.get("description") or normalized_fields.get("summary") or ""),
        },
        "refs": {
            "source_observation_id": source_observation.get("observation_id"),
            "normalized_observation_id": normalized_observation.get("normalized_observation_id"),
            "source_cache_entry_id": source_cache_entry.get("entry_id"),
            "evidence_id": evidence_id,
            "review_item_id": object_result.get("review_item_id"),
            "review_decision_id": review_decision_id,
            "public_index_record_id": record_id,
            "evidence_summary_id": EVIDENCE_SUMMARY_PACKET_ID,
            "source_provenance_packet_id": SOURCE_PROVENANCE_PACKET_ID,
        },
        "index_inclusion_reason": "accepted local fixture review decision",
        "limitations": _unique_strings(object_result.get("limitations", [])),
        "local_only": True,
        "fixture_only": True,
    }

    evidence_summary_packet = {
        "schema_version": "eureka.evidence_summary_packet.v0",
        "packet_id": EVIDENCE_SUMMARY_PACKET_ID,
        "evidence_id": evidence_id,
        "claim_type": evidence_record.get("claim_kind"),
        "subject_id": artifact_id,
        "claim_subject": evidence_record.get("claim_subject"),
        "source_id": source_id,
        "source_reference": source_reference,
        "observation_id": evidence_record.get("observation_id"),
        "normalized_observation_id": evidence_record.get("normalized_observation_id"),
        "source_cache_entry_id": evidence_record.get("source_cache_entry_id"),
        "review": {
            "decision_id": review_decision_id,
            "decision_kind": review_decision.get("decision_kind"),
            "decision_status": review_status,
            "actor": review_decision.get("decision_actor"),
            "accepted_for_local_index": review_status == "accepted",
        },
        "confidence": evidence_candidate.get("confidence"),
        "warnings": _unique_strings(
            list(evidence_candidate.get("warnings", []) or []) + list(evidence_record.get("warnings", []) or [])
        ),
        "gaps": (),
        "local_only": True,
        "fixture_only": True,
    }

    source_provenance_packet = {
        "schema_version": "eureka.source_provenance_packet.v0",
        "packet_id": SOURCE_PROVENANCE_PACKET_ID,
        "source_id": source_id,
        "source_family": source_record.get("source_family"),
        "trust_lane": source_record.get("trust_lane"),
        "source_reference": source_reference,
        "observed_at": FIXTURE_RESPONSE_TIMESTAMP,
        "fixture_only": True,
        "local_only": True,
        "no_live": {
            "network_calls": proof.get("network_calls"),
            "provider_model_calls": proof.get("provider_model_calls"),
            "live_source_probes": proof.get("live_source_probes"),
            "source_sync": proof.get("source_sync"),
        },
        "limitations": _unique_strings(source_record.get("limitations", [])),
    }

    absence_packet = {
        "schema_version": "eureka.absence_packet.v0",
        "packet_id": ABSENCE_PACKET_ID,
        "query": ABSENCE_QUERY,
        "result_count": int(absence.get("result_count", -1) or 0),
        "checked_sources": tuple(absence.get("checked_sources", []) or []),
        "checked_index": "isolated_fixture_reviewed_index",
        "reason": "no local reviewed fixture record matched the query",
        "known_gaps": (
            "local fixture index only",
            "does not inspect live sources",
            "does not prove global absence",
        ),
        "next_actions": ("inspect_checked_sources", "broaden_source_scope_in_future_reviewed_task"),
        "limitations": _unique_strings(absence.get("limitations", [])),
        "local_only": True,
        "fixture_only": True,
    }

    return {
        "schema_version": SURFACE_SCHEMA_VERSION,
        "result_packet": result_packet,
        "object_detail_packet": object_detail_packet,
        "evidence_summary_packet": evidence_summary_packet,
        "source_provenance_packet": source_provenance_packet,
        "absence_packet": absence_packet,
    }


def validate_inspection_surface_packets(surface_packets: Mapping[str, Any], report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if surface_packets.get("schema_version") != SURFACE_SCHEMA_VERSION:
        errors.append(f"surface packet schema_version must be {SURFACE_SCHEMA_VERSION}")
    required_packets = {
        "result_packet",
        "object_detail_packet",
        "evidence_summary_packet",
        "source_provenance_packet",
        "absence_packet",
    }
    missing = sorted(required_packets - set(surface_packets))
    if missing:
        errors.append("missing surface packets: " + ", ".join(missing))
        return errors

    result_packet = _mapping_at(surface_packets, "result_packet")
    object_packet = _mapping_at(surface_packets, "object_detail_packet")
    evidence_packet = _mapping_at(surface_packets, "evidence_summary_packet")
    source_packet = _mapping_at(surface_packets, "source_provenance_packet")
    absence_packet = _mapping_at(surface_packets, "absence_packet")
    evidence_record = _mapping_at(report, "evidence_record")
    review_decision = _mapping_at(report, "review_decision")
    object_result = _mapping_at(report, "object_result")

    results = result_packet.get("results", [])
    if result_packet.get("query") != POSITIVE_QUERY or int(result_packet.get("result_count", 0) or 0) != 1:
        errors.append("result packet must describe the positive query and one result")
    if not isinstance(results, list) or len(results) != 1:
        errors.append("result packet must contain exactly one result")
    else:
        result = results[0]
        if result.get("evidence_id") != evidence_record.get("evidence_id"):
            errors.append("result packet evidence ref does not match evidence record")
        if result.get("review_status") != "accepted":
            errors.append("result packet review status must be accepted")
        if result.get("object_id") != object_result.get("record_id"):
            errors.append("result packet object ref does not match object result")
    if object_packet.get("refs", {}).get("evidence_id") != evidence_record.get("evidence_id"):
        errors.append("object packet evidence ref does not match evidence record")
    if object_packet.get("refs", {}).get("review_decision_id") != review_decision.get("decision_id"):
        errors.append("object packet review decision ref does not match review decision")
    if evidence_packet.get("evidence_id") != evidence_record.get("evidence_id"):
        errors.append("evidence summary packet evidence ref does not match evidence record")
    if evidence_packet.get("review", {}).get("decision_status") != "accepted":
        errors.append("evidence summary packet review status must be accepted")
    if source_packet.get("source_id") != report.get("source_record", {}).get("id"):
        errors.append("source provenance packet source id does not match source record")
    if source_packet.get("no_live", {}).get("network_calls") is not False:
        errors.append("source provenance packet must prove no network calls")
    if absence_packet.get("query") != ABSENCE_QUERY or int(absence_packet.get("result_count", -1) or 0) != 0:
        errors.append("absence packet must describe the absence query and zero results")
    for packet_name in required_packets:
        packet = _mapping_at(surface_packets, packet_name)
        if packet.get("local_only") is not True or packet.get("fixture_only") is not True:
            errors.append(f"{packet_name} must be marked local_only and fixture_only")
    return errors


def build_reviewed_index_artifact(report: Mapping[str, Any]) -> dict[str, Any]:
    """Build the deterministic persisted local reviewed-index artifact."""

    records = [_artifact_record(record) for record in report.get("public_index_records", []) or []]
    records.sort(key=lambda record: str(record.get("record_id", "")))
    source_record = _mapping_at(report, "source_record")
    evidence_record = _mapping_at(report, "evidence_record")
    review_item = _mapping_at(report, "review_item")
    review_decision = _mapping_at(report, "review_decision")
    surface_packets = _mapping_at(report, "surface_packets")
    absence = _mapping_at(report, "absence")
    artifact = {
        "schema_version": REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION,
        "artifact_id": REVIEWED_INDEX_ARTIFACT_ID,
        "artifact_kind": "local_reviewed_fixture_index_candidate",
        "generated_by": REVIEWED_INDEX_BUILDER_ID,
        "generated_at": FIXTURE_RESPONSE_TIMESTAMP,
        "source_fixture_id": "fixture://q58/demo-project",
        "source_fixture_name": "demo-project",
        "local_only": True,
        "fixture_only": True,
        "production_public_index": False,
        "public_index_mutation": False,
        "records": records,
        "record_count": len(records),
        "source_refs": {
            "source_id": source_record.get("id"),
            "source_family": source_record.get("source_family"),
            "source_observation_id": report.get("source_observation", {}).get("observation_id"),
            "normalized_observation_id": report.get("normalized_observation", {}).get("normalized_observation_id"),
            "source_cache_entry_id": report.get("source_cache_entry", {}).get("entry_id"),
        },
        "evidence_refs": {
            "evidence_id": evidence_record.get("evidence_id"),
            "claim_type": evidence_record.get("claim_kind"),
            "claim_subject": evidence_record.get("claim_subject"),
        },
        "review_refs": {
            "review_item_id": review_item.get("review_item_id"),
            "review_decision_id": review_decision.get("decision_id"),
            "review_status": review_decision.get("decision_status"),
            "review_decision_kind": review_decision.get("decision_kind"),
        },
        "surface_packet_refs": {
            "result_packet_id": _mapping_at(surface_packets, "result_packet").get("packet_id"),
            "object_detail_packet_id": _mapping_at(surface_packets, "object_detail_packet").get("packet_id"),
            "evidence_summary_packet_id": _mapping_at(surface_packets, "evidence_summary_packet").get("packet_id"),
            "source_provenance_packet_id": _mapping_at(surface_packets, "source_provenance_packet").get("packet_id"),
            "absence_packet_id": _mapping_at(surface_packets, "absence_packet").get("packet_id"),
        },
        "surface_packets": dict(surface_packets),
        "absence_metadata": {
            "query": absence.get("query"),
            "result_count": absence.get("result_count"),
            "checked_sources": list(absence.get("checked_sources", []) or []),
            "checked_index": "isolated_fixture_reviewed_index",
            "scope": "local fixture reviewed index only",
            "does_not_prove_global_absence": True,
        },
        "no_live": {
            "network_calls": False,
            "provider_model_calls": False,
            "live_source_probes": False,
            "source_sync": False,
        },
        "limitations": [
            "fixture-only reviewed index artifact",
            "not a production public index",
            "not live-source support",
        ],
    }
    artifact["artifact_hash"] = _artifact_hash(artifact)
    return artifact


def validate_reviewed_index_artifact(artifact: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if artifact.get("schema_version") != REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION:
        errors.append(f"artifact schema_version must be {REVIEWED_INDEX_ARTIFACT_SCHEMA_VERSION}")
    if artifact.get("artifact_id") != REVIEWED_INDEX_ARTIFACT_ID:
        errors.append(f"artifact_id must be {REVIEWED_INDEX_ARTIFACT_ID}")
    if artifact.get("artifact_kind") != "local_reviewed_fixture_index_candidate":
        errors.append("artifact kind must be local_reviewed_fixture_index_candidate")
    if artifact.get("local_only") is not True or artifact.get("fixture_only") is not True:
        errors.append("artifact must be marked local_only and fixture_only")
    if artifact.get("production_public_index") is not False:
        errors.append("artifact must not be marked as production public index")
    if artifact.get("public_index_mutation") is not False:
        errors.append("artifact must not record public index mutation")
    no_live = _mapping_at(artifact, "no_live")
    for key in ("network_calls", "provider_model_calls", "live_source_probes", "source_sync"):
        if no_live.get(key) is not False:
            errors.append(f"artifact no_live.{key} must be False")
    records = artifact.get("records", [])
    if not isinstance(records, list):
        errors.append("artifact records must be a list")
        records = []
    if int(artifact.get("record_count", -1) or 0) != len(records):
        errors.append("artifact record_count must match records length")
    if not records:
        errors.append("artifact must contain at least one reviewed fixture record")
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("artifact record must be an object")
            continue
        for key in (
            "record_id",
            "artifact_id",
            "title",
            "source_id",
            "source_cache_entry_id",
            "evidence_id",
            "review_item_id",
            "review_decision_id",
            "review_status",
            "searchable_text",
        ):
            if not record.get(key):
                errors.append(f"artifact record missing required field: {key}")
        if record.get("review_status") != "accepted":
            errors.append("artifact records must be accepted before indexing")
        if record.get("local_only") is not True or record.get("fixture_only") is not True:
            errors.append("artifact records must be local_only and fixture_only")
    source_refs = _mapping_at(artifact, "source_refs")
    evidence_refs = _mapping_at(artifact, "evidence_refs")
    review_refs = _mapping_at(artifact, "review_refs")
    if not source_refs.get("source_id") or not source_refs.get("source_cache_entry_id"):
        errors.append("artifact source refs must include source and cache ids")
    if not evidence_refs.get("evidence_id"):
        errors.append("artifact evidence refs must include evidence id")
    if review_refs.get("review_status") != "accepted":
        errors.append("artifact review refs must record accepted status")
    surface_packets = _mapping_at(artifact, "surface_packets")
    if surface_packets.get("schema_version") != SURFACE_SCHEMA_VERSION:
        errors.append(f"artifact surface packets must use {SURFACE_SCHEMA_VERSION}")
    absence_metadata = _mapping_at(artifact, "absence_metadata")
    if absence_metadata.get("query") != ABSENCE_QUERY or int(absence_metadata.get("result_count", -1) or 0) != 0:
        errors.append("artifact absence metadata must describe the bounded absence query")
    expected_hash = _artifact_hash(artifact)
    if artifact.get("artifact_hash") != expected_hash:
        errors.append("artifact hash is not deterministic for artifact content")
    return errors


def write_reviewed_index_artifact(path: str | Path, artifact: Mapping[str, Any]) -> None:
    errors = validate_reviewed_index_artifact(artifact)
    if errors:
        raise ValueError("reviewed index artifact validation failed: " + "; ".join(errors))
    write_json(path, artifact)


def load_reviewed_index_artifact(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise ValueError("reviewed index artifact is missing; rebuild fixture slice")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("reviewed index artifact is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("reviewed index artifact must be a JSON object")
    errors = validate_reviewed_index_artifact(payload)
    if errors:
        raise ValueError("reviewed index artifact validation failed: " + "; ".join(errors))
    return payload


def search_reviewed_index_artifact(artifact: Mapping[str, Any], query: str, limit: int = 20) -> dict[str, Any]:
    errors = validate_reviewed_index_artifact(artifact)
    if errors:
        raise ValueError("reviewed index artifact validation failed: " + "; ".join(errors))
    terms = [item.lower() for item in query.split() if item.strip()]
    results: list[dict[str, Any]] = []
    for record in sorted(artifact.get("records", []) or [], key=lambda item: str(item.get("record_id", ""))):
        if record.get("review_status") != "accepted":
            continue
        searchable_text = str(record.get("searchable_text", "")).lower()
        matched_terms = [term for term in terms if term in searchable_text]
        if not terms or not matched_terms:
            continue
        results.append(
            {
                "record_id": record.get("record_id"),
                "object_id": record.get("record_id"),
                "artifact_id": record.get("artifact_id"),
                "title": record.get("title"),
                "source_id": record.get("source_id"),
                "evidence_id": record.get("evidence_id"),
                "review_decision_id": record.get("review_decision_id"),
                "review_status": record.get("review_status"),
                "matched_terms": matched_terms,
                "local_only": True,
                "fixture_only": True,
            }
        )
        if len(results) >= limit:
            break
    return {
        "schema_version": "eureka.persisted_reviewed_index_search.v0",
        "artifact_id": artifact.get("artifact_id"),
        "query": query,
        "result_count": len(results),
        "results": results,
        "local_only": True,
        "fixture_only": True,
    }


def get_reviewed_index_artifact_object(artifact: Mapping[str, Any], object_id: str) -> dict[str, Any]:
    errors = validate_reviewed_index_artifact(artifact)
    if errors:
        raise ValueError("reviewed index artifact validation failed: " + "; ".join(errors))
    object_packet = _mapping_at(artifact, "surface_packets", "object_detail_packet")
    if object_packet.get("object_id") == object_id:
        return {
            "schema_version": "eureka.persisted_reviewed_index_object.v0",
            "artifact_id": artifact.get("artifact_id"),
            "object_id": object_id,
            "found": True,
            "object_detail_packet": dict(object_packet),
            "local_only": True,
            "fixture_only": True,
        }
    return {
        "schema_version": "eureka.persisted_reviewed_index_object.v0",
        "artifact_id": artifact.get("artifact_id"),
        "object_id": object_id,
        "found": False,
        "reason": "object id not present in local reviewed fixture artifact",
        "local_only": True,
        "fixture_only": True,
    }


def absence_from_reviewed_index_artifact(artifact: Mapping[str, Any], query: str) -> dict[str, Any]:
    search_packet = search_reviewed_index_artifact(artifact, query, limit=1)
    source_refs = _mapping_at(artifact, "source_refs")
    return {
        "schema_version": "eureka.persisted_reviewed_index_absence.v0",
        "artifact_id": artifact.get("artifact_id"),
        "query": query,
        "result_count": search_packet.get("result_count"),
        "checked_index": artifact.get("artifact_id"),
        "checked_sources": [source_refs.get("source_id")] if source_refs.get("source_id") else [],
        "reason": "no local reviewed fixture artifact record matched the query",
        "known_gaps": [
            "local fixture reviewed index artifact only",
            "does not inspect live sources",
            "does not prove global absence",
        ],
        "local_only": True,
        "fixture_only": True,
    }


def no_live_no_mutation_claims(output_root: Path) -> dict[str, Any]:
    return {
        "network_calls": False,
        "provider_model_calls": False,
        "live_source_probes": False,
        "crawling_downloading_scraping": False,
        "source_sync": False,
        "registry_mutation": False,
        "production_source_cache_writes": False,
        "production_evidence_ledger_writes": False,
        "production_public_index_writes": False,
        "site_deploy": False,
        "release_publish": False,
        "branch_mutation": False,
        "canonical_product_store_writes": False,
        "fixture_store_root": str(output_root),
        "fixture_store_root_isolated": True,
    }


def resolve_output_root(output_root: str | Path | None = None) -> Path:
    if output_root is None:
        return Path(tempfile.mkdtemp(prefix="eureka-q58-fixture-slice-")).resolve()
    root = Path(output_root)
    if not root.is_absolute():
        root = Path.cwd() / root
    root = root.resolve()
    validate_output_root(root)
    return root


def validate_output_root(root: Path) -> None:
    cwd = Path.cwd().resolve()
    try:
        relative = root.relative_to(cwd)
    except ValueError:
        return
    parts = relative.parts
    if not parts:
        raise ValueError("output root must not be the repository root")
    if parts[0] in FORBIDDEN_OUTPUT_ROOTS:
        raise ValueError(f"refusing product or private output root: {relative.as_posix()}")


def _fixture_policy() -> SourcePolicy:
    return SourcePolicy(
        allowed_operations=("metadata_observation",),
        limitations=("fixture/local-only source observation",),
    )


def _required_no_live_flags() -> dict[str, bool]:
    return {
        "network_calls": False,
        "provider_model_calls": False,
        "live_source_probes": False,
        "crawling_downloading_scraping": False,
        "source_sync": False,
        "registry_mutation": False,
        "production_source_cache_writes": False,
        "production_evidence_ledger_writes": False,
        "production_public_index_writes": False,
        "site_deploy": False,
        "release_publish": False,
        "branch_mutation": False,
        "canonical_product_store_writes": False,
        "fixture_store_root_isolated": True,
    }


def _mapping_at(mapping: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, Mapping):
            return {}
        current = current.get(key, {})
    return current if isinstance(current, Mapping) else {}


def _artifact_record(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized_fields = dict(record.get("normalized_fields", {}) or {})
    return {
        "record_id": record.get("record_id") or record.get("id"),
        "object_id": record.get("record_id") or record.get("id"),
        "artifact_id": normalized_fields.get("artifact_id") or record.get("record_id") or record.get("id"),
        "title": record.get("title"),
        "description": record.get("description"),
        "version": normalized_fields.get("version"),
        "source_id": record.get("source_id"),
        "source_cache_entry_id": record.get("source_cache_entry_id"),
        "evidence_id": record.get("evidence_id"),
        "review_item_id": record.get("review_item_id"),
        "review_decision_id": record.get("review_decision_id"),
        "review_status": "accepted",
        "status": "reviewed_local_fixture_index_candidate",
        "source_family": record.get("source_family"),
        "trust_lane": record.get("trust_lane"),
        "normalized_fields": normalized_fields,
        "searchable_text": record.get("searchable_text"),
        "limitations": list(record.get("limitations", []) or []),
        "warnings": list(record.get("warnings", []) or []),
        "created_at": FIXTURE_RESPONSE_TIMESTAMP,
        "updated_at": FIXTURE_RESPONSE_TIMESTAMP,
        "local_only": True,
        "fixture_only": True,
    }


def _artifact_hash(artifact: Mapping[str, Any]) -> str:
    basis = dict(artifact)
    basis.pop("artifact_hash", None)
    return "sha256:" + _sha256_bytes(_canonical_json_bytes(basis))


def _file_sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _unique_strings(values: Any) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        return ()
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return tuple(result)


def write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
