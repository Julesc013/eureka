from __future__ import annotations

import unittest

from runtime.review import (
    ReviewLedgerDecisionRequest,
    ReviewLedgerError,
    build_review_item_from_fallback_summary,
    enqueue_fallback_review_item,
    record_review_ledger_decision,
    review_boundary_report,
)
from runtime.review.queue import ReviewQueueStatus, ReviewQueueStore


class ReviewLedgerTests(unittest.TestCase):
    def test_fallback_candidate_handoff_is_not_self_promoted(self) -> None:
        fallback = _fallback_candidate_summary()
        item = build_review_item_from_fallback_summary(fallback)

        self.assertEqual(item.subject_kind, "fallback_candidate")
        self.assertEqual(item.subject_id, "ia-meta-candidate:test")
        self.assertEqual(item.queue_status, ReviewQueueStatus.NEEDS_REVIEW)
        self.assertTrue(item.payload["review_required"])
        self.assertFalse(item.payload["self_promotion_allowed"])
        serialized = item.to_json()
        self.assertNotIn("accepted_truth", serialized)
        self.assertNotIn("public_index_mutated", serialized)
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(fallback["reviewed_record_created"])

    def test_boundary_report_blocks_candidate_fallback_and_source_self_promotion(self) -> None:
        report = review_boundary_report(_fallback_candidate_summary())

        self.assertFalse(report["candidate_can_self_promote"])
        self.assertFalse(report["fallback_can_self_promote"])
        self.assertFalse(report["source_observation_can_self_promote"])
        self.assertTrue(report["review_event_required_for_promotion"])
        self.assertFalse(report["public_projection_can_promote"])

    def test_promote_requires_review_item_confirmation_and_citation(self) -> None:
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            item = enqueue_fallback_review_item(store, _fallback_candidate_summary())

            with self.assertRaises(ReviewLedgerError):
                record_review_ledger_decision(
                    store,
                    ReviewLedgerDecisionRequest(
                        review_item_id=item.review_item_id,
                        decision="promote",
                        actor="operator:local",
                        fallback_refs=tuple(item.payload["fallback_refs"]),
                    ),
                )

            result = record_review_ledger_decision(
                store,
                ReviewLedgerDecisionRequest(
                    review_item_id=item.review_item_id,
                    decision="promote",
                    actor="operator:local",
                    source_observation_refs=tuple(item.payload["source_observation_refs"]),
                    fallback_refs=tuple(item.payload["fallback_refs"]),
                    local_only_confirmed=True,
                ),
            )

            fetched = store.get_review_item(item.review_item_id)
            decisions = store.list_decisions(item.review_item_id)
            events = store.list_events(item.review_item_id)

        payload = result.to_dict()
        self.assertEqual(payload["decision"], "promote")
        self.assertEqual(payload["queue_status"], "accepted")
        self.assertEqual(payload["resulting_status"], "verified")
        self.assertFalse(payload["reviewed_record_created"])
        self.assertFalse(payload["reviewed_index_mutated"])
        self.assertFalse(payload["public_index_mutated"])
        self.assertEqual(fetched.queue_status, ReviewQueueStatus.ACCEPTED)
        self.assertEqual(decisions[0].decision_kind.value, "accept")
        self.assertIn("srcobs:test", decisions[0].payload["source_observation_refs"])
        self.assertIn("decision_recorded", [event.event_kind.value for event in events])
        audit_events = [
            event for event in events if event.event_payload.get("ledger_event_kind") == "review_ledger_decision_context"
        ]
        self.assertEqual(1, len(audit_events))
        self.assertIn("srcobs:test", audit_events[0].event_payload["source_observation_refs"])

    def test_reject_records_audit_preserving_status_and_reason(self) -> None:
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            item = enqueue_fallback_review_item(store, _fallback_candidate_summary())
            result = record_review_ledger_decision(
                store,
                ReviewLedgerDecisionRequest(
                    review_item_id=item.review_item_id,
                    decision="reject",
                    actor="operator:local",
                    reason="wrong artifact family",
                    fallback_refs=tuple(item.payload["fallback_refs"]),
                ),
            )
            fetched = store.get_review_item(item.review_item_id)
            decision = store.list_decisions(item.review_item_id)[0]

        self.assertEqual(result.queue_status, "rejected")
        self.assertEqual(result.resulting_status, "rejected")
        self.assertEqual(fetched.queue_status, ReviewQueueStatus.REJECTED)
        self.assertEqual(decision.reason, "wrong artifact family")
        self.assertFalse(result.reviewed_record_created)
        self.assertFalse(result.public_index_mutated)

    def test_request_more_evidence_keeps_item_out_of_reviewed_projection(self) -> None:
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            item = enqueue_fallback_review_item(store, _fallback_need_summary())
            result = record_review_ledger_decision(
                store,
                ReviewLedgerDecisionRequest(
                    review_item_id=item.review_item_id,
                    decision="request_more_evidence",
                    actor="operator:local",
                    reason="need stronger source observation",
                    fallback_refs=tuple(item.payload["fallback_refs"]),
                ),
            )
            fetched = store.get_review_item(item.review_item_id)

        self.assertEqual(item.subject_kind, "fallback_need")
        self.assertEqual(result.queue_status, "needs_more_evidence")
        self.assertEqual(result.resulting_status, "need")
        self.assertEqual(fetched.queue_status, ReviewQueueStatus.NEEDS_MORE_EVIDENCE)
        self.assertFalse(result.reviewed_record_created)
        self.assertFalse(result.reviewed_index_mutated)

    def test_decision_requires_citation_or_rationale(self) -> None:
        with ReviewQueueStore.open(":memory:") as store:
            store.init()
            item = enqueue_fallback_review_item(store, _fallback_candidate_summary())

            with self.assertRaises(ReviewLedgerError):
                record_review_ledger_decision(
                    store,
                    ReviewLedgerDecisionRequest(
                        review_item_id=item.review_item_id,
                        decision="mark_near_miss",
                        actor="operator:local",
                    ),
                )


def _fallback_candidate_summary() -> dict[str, object]:
    return {
        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
        "mode": "indexless_live_search_fallback",
        "status": "candidate",
        "trigger": "local_lookup_no_results",
        "query": "missing",
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_observation": {
            "schema_version": "eureka.source_observation.summary.v0",
            "observation_id": "srcobs:test",
            "status": "succeeded",
            "source_id": "internet_archive_metadata",
            "source_family": "internet_archive",
            "accepted_truth": False,
            "verified": False,
            "review_required": True,
        },
        "candidate_count": 1,
        "candidates": [
            {
                "candidate_id": "ia-meta-candidate:test",
                "status": "candidate",
                "title": "Archive.org metadata candidate",
                "accepted_truth": False,
                "verified": False,
                "review_required": True,
            }
        ],
        "need_count": 0,
        "needs": [],
        "accepted_truth": False,
        "verified": False,
        "review_required": True,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


def _fallback_need_summary() -> dict[str, object]:
    return {
        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
        "mode": "indexless_live_search_fallback",
        "status": "need",
        "trigger": "local_lookup_no_results",
        "query": "missing",
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
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
        "accepted_truth": False,
        "verified": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


if __name__ == "__main__":
    unittest.main()
