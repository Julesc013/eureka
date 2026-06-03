from __future__ import annotations

import unittest

from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.local.service.workbench_run_review_projection import (
    PUBLIC_DISALLOWED_ACTIONS,
    create_review_item_from_fallback_for_workbench,
    project_workbench_run_review,
    public_surface_operator_action_audit,
)
from runtime.review import ReviewLedgerDecisionRequest, record_review_ledger_decision
from runtime.review.queue import ReviewQueueStore


class WorkbenchRunReviewProjectionTests(unittest.TestCase):
    def test_projection_includes_candidate_fallback_without_verification(self) -> None:
        run = _run_with_fallback(_candidate_fallback())

        projection = project_workbench_run_review(run)

        self.assertEqual(projection["projection_profile"], "operator_workbench")
        self.assertEqual(projection["local_lookup"]["status"], "local_lookup_insufficient")
        fallback = projection["fallback_summary"]
        self.assertEqual(fallback["status"], "candidate")
        self.assertEqual(fallback["candidate_count"], 1)
        self.assertFalse(fallback["verified"])
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(fallback["reviewed_index_mutated"])
        candidate = fallback["candidates"][0]
        self.assertEqual(candidate["canonical_status"], "candidate")
        self.assertFalse(candidate["verified"])
        self.assertFalse(candidate["accepted_truth"])
        action_ids = {action["action_id"]: action for action in projection["operator_actions"]}
        self.assertTrue(action_ids["inspect_fallback_summary"]["enabled"])
        self.assertTrue(action_ids["inspect_candidate"]["enabled"])
        self.assertTrue(action_ids["create_review_item_from_candidate"]["enabled"])
        self.assertFalse(action_ids["promote"]["enabled"])
        self.assertFalse(projection["boundary_report"]["public_projection_can_change_review_state"])

    def test_need_policy_blocked_and_unavailable_states_are_visible(self) -> None:
        cases = (
            ("need", _need_fallback(), "inspect_need"),
            ("policy_blocked", _policy_blocked_fallback(), "mark_policy_blocked"),
            ("unavailable", _unavailable_fallback(), "request_more_evidence"),
        )
        for expected_status, fallback, blocked_action in cases:
            with self.subTest(status=expected_status):
                projection = project_workbench_run_review(_run_with_fallback(fallback))
                fallback_projection = projection["fallback_summary"]
                self.assertEqual(fallback_projection["status"], expected_status)
                self.assertFalse(fallback_projection["verified"])
                self.assertFalse(fallback_projection["reviewed_record_created"])
                if expected_status == "need":
                    self.assertEqual(fallback_projection["needs"][0]["canonical_status"], "need")
                actions = {action["action_id"]: action for action in projection["operator_actions"]}
                if expected_status == "need":
                    self.assertTrue(actions["create_review_item_from_need"]["enabled"])
                else:
                    self.assertFalse(actions[blocked_action]["enabled"])

    def test_review_item_creation_is_private_and_does_not_mutate_indexes(self) -> None:
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            candidate_result = create_review_item_from_fallback_for_workbench(
                store,
                _run_with_fallback(_candidate_fallback()),
            )
            public_result = create_review_item_from_fallback_for_workbench(
                store,
                _run_with_fallback(_need_fallback()),
                projection_profile="public_web",
            )

            stored = store.get_review_item(candidate_result["review_item"]["review_item_id"])

        self.assertEqual(candidate_result["status"], "stored")
        self.assertTrue(candidate_result["review_item_created"])
        self.assertIsNotNone(stored)
        self.assertEqual(candidate_result["review_item"]["subject_kind"], "fallback_candidate")
        self.assertFalse(candidate_result["reviewed_record_created"])
        self.assertFalse(candidate_result["reviewed_index_mutated"])
        self.assertEqual(public_result["status"], "blocked")
        self.assertFalse(public_result["review_item_created"])

    def test_review_ledger_decision_and_audit_events_are_visible(self) -> None:
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            created = create_review_item_from_fallback_for_workbench(
                store,
                _run_with_fallback(_candidate_fallback()),
            )
            review_item = created["review_item"]
            record_review_ledger_decision(
                store,
                ReviewLedgerDecisionRequest(
                    review_item_id=review_item["review_item_id"],
                    decision="promote",
                    actor="operator:workbench",
                    source_observation_refs=tuple(review_item["payload"]["source_observation_refs"]),
                    fallback_refs=tuple(review_item["payload"]["fallback_refs"]),
                    local_only_confirmed=True,
                ),
            )

            projection = project_workbench_run_review(
                _run_with_fallback(_candidate_fallback()),
                review_store=store,
            )

        review = projection["review_ledger"]
        self.assertTrue(review["review_item_present"])
        self.assertEqual(review["review_item_count"], 1)
        self.assertEqual(review["decision_count"], 1)
        self.assertEqual(review["decisions"][0]["decision_kind"], "accept")
        self.assertEqual(review["review_items"][0]["queue_status"], "accepted")
        self.assertGreaterEqual(review["audit_event_count"], 2)
        self.assertFalse(review["reviewed_record_created"])
        self.assertFalse(review["public_index_mutated"])
        actions = {action["action_id"]: action for action in projection["operator_actions"]}
        self.assertTrue(actions["inspect_review_event"]["enabled"])

    def test_public_projection_and_audit_hide_operator_actions(self) -> None:
        projection = project_workbench_run_review(
            _run_with_fallback(_candidate_fallback()),
            projection_profile="public_web",
        )

        self.assertEqual(projection["operator_actions"], [])
        audit = public_surface_operator_action_audit(projection)

        self.assertEqual(audit["status"], "pass")
        self.assertFalse(audit["operator_actions_exposed_publicly"])
        serialized = repr(projection)
        for action in PUBLIC_DISALLOWED_ACTIONS:
            self.assertNotIn(action, serialized)


def _run_with_fallback(fallback: dict[str, object]) -> ResolutionRunRecord:
    return ResolutionRunRecord(
        run_id="run-deterministic-search-0001",
        run_kind="deterministic_search",
        requested_value=str(fallback.get("query", "missing")),
        status="completed",
        started_at="2026-04-24T00:00:00+00:00",
        completed_at="2026-04-24T00:00:00+00:00",
        checked_source_ids=(),
        checked_source_families=(),
        fallback_summary=fallback,
    )


def _candidate_fallback() -> dict[str, object]:
    return {
        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
        "mode": "indexless_live_search_fallback",
        "status": "candidate",
        "trigger": "local_lookup_no_results",
        "query": "missing",
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_allowlisted": True,
        "fallback_enabled": True,
        "reason_codes": ["fallback_candidates_available"],
        "budget": {"max_requests": 1, "candidate_limit": 5, "timeout_seconds": 5},
        "source_observation": {
            "schema_version": "eureka.source_observation.summary.v0",
            "observation_id": "srcobs:test",
            "status": "succeeded",
            "source_id": "internet_archive_metadata",
            "source_family": "internet_archive",
            "candidate_count": 1,
            "verified": False,
            "accepted_truth": False,
            "review_required": True,
        },
        "candidate_count": 1,
        "candidates": [
            {
                "candidate_id": "ia-meta-candidate:test",
                "status": "candidate",
                "title": "Archive.org metadata candidate",
                "verified": False,
                "accepted_truth": False,
                "review_required": True,
            }
        ],
        "need_count": 0,
        "needs": [],
        "accepted_truth": False,
        "verified": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


def _need_fallback() -> dict[str, object]:
    fallback = _candidate_fallback()
    fallback.update(
        {
            "status": "need",
            "reason_codes": ["fallback_no_candidates"],
            "candidate_count": 0,
            "candidates": [],
            "need_count": 1,
            "needs": [
                {
                    "need_id": "search-need:test",
                    "status": "need",
                    "query": "missing",
                    "verified": False,
                    "review_required": False,
                }
            ],
        }
    )
    return fallback


def _policy_blocked_fallback() -> dict[str, object]:
    fallback = _candidate_fallback()
    fallback.update(
        {
            "status": "policy_blocked",
            "reason_codes": ["source_family_not_allowlisted"],
            "candidate_count": 0,
            "candidates": [],
        }
    )
    return fallback


def _unavailable_fallback() -> dict[str, object]:
    fallback = _candidate_fallback()
    fallback.update(
        {
            "status": "unavailable",
            "failure_reason": "source_timeout",
            "reason_codes": ["source_timeout"],
            "candidate_count": 0,
            "candidates": [],
        }
    )
    return fallback


if __name__ == "__main__":
    unittest.main()
