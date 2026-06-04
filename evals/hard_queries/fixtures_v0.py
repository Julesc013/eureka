"""Synthetic hard-query fixture cases."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from runtime.engine.interfaces.public import ResolutionRunRecord


SYNTHETIC_FIXTURE_DISCLAIMER = (
    "Synthetic hard-query fixtures are evaluation pressure only. "
    "They are not evidence. They are not reviewed records. "
    "They do not promote corpus truth."
)

FIXED_TIME = "2026-06-04T00:00:00+00:00"


def fixture_cases() -> tuple[dict[str, Any], ...]:
    return (
        _case(
            query_id="hq_windows_7_apps",
            query_text="Windows 7 apps",
            expected_status="candidate",
            title="Windows 7 compatible utility candidate",
            reason_codes=("fallback_candidates_available", "compatibility_scope_visible"),
            candidate_id="hq-candidate-windows-7-apps",
            candidate_title="Candidate Windows 7 utility package",
            evidence_summary="Synthetic source observation has Windows 7 compatibility hints.",
        ),
        _case(
            query_id="hq_driver_win98",
            query_text="driver for Win98",
            expected_status="need",
            title="Hardware model needed for Win98 driver search",
            reason_codes=("hardware_identifier_missing", "source_scope_not_enough"),
            need_id="hq-need-driver-win98-hardware",
            need_title="Need vendor and device model before driver candidate can be useful",
            evidence_summary="Synthetic fixture records ambiguity around missing hardware identity.",
        ),
        _case(
            query_id="hq_blue_ftp_client_xp",
            query_text="old blue FTP client for XP",
            expected_status="near_miss",
            title="Old \"Blue\" FTP <client> near miss",
            reason_codes=("visual_clue_uncertain", "platform_scope_visible"),
            candidate_id="hq-near-miss-blue-ftp-xp",
            candidate_title="Plausible XP FTP <client>; \"blue\" visual clue not supported",
            evidence_summary="Synthetic fixture keeps the blue clue uncertain instead of promoting identity.",
        ),
        _case(
            query_id="hq_sound_blaster_ct1740_manual",
            query_text="manual for Sound Blaster CT1740",
            expected_status="candidate",
            title="Sound Blaster CT1740 manual candidate",
            reason_codes=("manual_candidate_available", "model_identifier_visible"),
            candidate_id="hq-candidate-ct1740-manual",
            candidate_title="Candidate CT1740 manual document",
            evidence_summary="Synthetic source observation includes CT1740 model text and document type.",
        ),
        _case(
            query_id="hq_firefox_last_xp",
            query_text="latest Firefox before XP support ended",
            expected_status="policy_blocked",
            title="Firefox XP support answer requires reviewed evidence",
            reason_codes=("support_window_evidence_required", "public_acquisition_action_blocked"),
            policy_block_reason="Fixture blocks public acquisition/version certainty until reviewed evidence exists.",
            evidence_summary="Synthetic fixture represents a blocked/degraded public state only.",
        ),
        _case(
            query_id="hq_ray_tracing_1994_magazine",
            query_text="article about ray tracing in a 1994 magazine",
            expected_status="unavailable",
            title="Article scan scope unavailable",
            reason_codes=("publication_title_missing", "article_scan_capability_gap"),
            unavailable_reason="Fixture cannot identify article, issue, or page without more scope.",
            evidence_summary="Synthetic fixture exposes capability/source limits without claiming absence.",
        ),
    )


def fixture_case_by_query_id(query_id: str) -> dict[str, Any]:
    for fixture in fixture_cases():
        if fixture["query_id"] == query_id:
            return deepcopy(fixture)
    raise KeyError(query_id)


def resolution_run_for_fixture(fixture: Mapping[str, Any]) -> ResolutionRunRecord:
    query_id = str(fixture["query_id"])
    return ResolutionRunRecord(
        run_id=f"run-{query_id}",
        run_kind="hard_query_fixture_eval",
        requested_value=str(fixture["query_text"]),
        status="completed",
        started_at=FIXED_TIME,
        completed_at=FIXED_TIME,
        checked_source_ids=(),
        checked_source_families=(),
        fallback_summary=deepcopy(dict(fixture["fallback_summary"])),
    )


def _case(
    *,
    query_id: str,
    query_text: str,
    expected_status: str,
    title: str,
    reason_codes: tuple[str, ...],
    evidence_summary: str,
    candidate_id: str | None = None,
    candidate_title: str | None = None,
    need_id: str | None = None,
    need_title: str | None = None,
    policy_block_reason: str | None = None,
    unavailable_reason: str | None = None,
) -> dict[str, Any]:
    fallback = {
        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
        "mode": "hard_query_eval_fixture",
        "status": expected_status,
        "trigger": "synthetic_hard_query_fixture",
        "query": query_text,
        "source_id": "synthetic_hard_query_fixture",
        "source_family": "eval_fixture",
        "source_allowlisted": True,
        "fallback_enabled": True,
        "reason_codes": list(reason_codes),
        "title": title,
        "evidence_summary": evidence_summary,
        "public_action_posture": {
            "allowed": ["view", "inspect_evidence", "cite", "promote", "download"],
            "blocked_reason": "public output keeps unsafe actions unavailable",
        },
        "candidate_count": 0,
        "candidates": [],
        "need_count": 0,
        "needs": [],
        "accepted_truth": False,
        "verified": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "live_source_calls": False,
    }
    if candidate_id:
        fallback["candidate_count"] = 1
        fallback["candidates"] = [
            {
                "candidate_id": candidate_id,
                "status": "candidate" if expected_status != "near_miss" else "near_miss",
                "title": candidate_title or title,
                "summary": evidence_summary,
                "verified": False,
                "accepted_truth": False,
                "public_actions": ["view", "inspect_evidence", "cite", "promote", "download"],
            }
        ]
    if need_id:
        fallback["need_count"] = 1
        fallback["needs"] = [
            {
                "need_id": need_id,
                "status": "need",
                "title": need_title or title,
                "summary": evidence_summary,
                "verified": False,
                "accepted_truth": False,
                "public_actions": ["view", "inspect_evidence", "request_more_evidence"],
            }
        ]
    if policy_block_reason:
        fallback["policy_block_reason"] = policy_block_reason
    if unavailable_reason:
        fallback["unavailable_reason"] = unavailable_reason
    return {
        "schema_version": "hard_query_fixture.v0",
        "fixture_disclaimer": SYNTHETIC_FIXTURE_DISCLAIMER,
        "query_id": query_id,
        "query_text": query_text,
        "expected_status": expected_status,
        "expected_summary_terms": tuple(reason_codes),
        "live_source_calls": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "fallback_summary": fallback,
    }
