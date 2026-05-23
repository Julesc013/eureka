import tempfile
import unittest
from pathlib import Path

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.review import record_review_decision
from runtime.local.review.decisions import LocalReviewDecisionRequest, validate_decision_request
from runtime.local.review.errors import LocalReviewDecisionError
from scripts.eureka_init_instance import initialize_instance
from scripts.validate_local_review_rebuild import seed_review_records


def make_runtime(tmp: str):
    instance = Path(tmp) / "eureka-instance"
    result = initialize_instance(instance)
    assert result["status"] in {"pass", "pass_with_warnings"}
    runtime = open_local_appliance(instance)
    seed = seed_review_records(runtime)
    return runtime, seed


class LocalReviewDecisionTests(unittest.TestCase):
    def test_accept_requires_local_only_confirmation(self) -> None:
        request = LocalReviewDecisionRequest(
            review_item_id="rvi_test",
            decision="accept",
            reason=None,
            operator_label="operator",
            local_only_confirmed=False,
        )

        with self.assertRaises(LocalReviewDecisionError):
            validate_decision_request(request)

    def test_reject_block_and_request_more_evidence_require_reason(self) -> None:
        for decision in ("reject", "block", "request_more_evidence"):
            request = LocalReviewDecisionRequest(
                review_item_id="rvi_test",
                decision=decision,
                reason=None,
                operator_label="operator",
                local_only_confirmed=False,
            )
            with self.assertRaises(LocalReviewDecisionError, msg=decision):
                validate_decision_request(request)

    def test_note_only_does_not_change_acceptance_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime, seed = make_runtime(tmp)
            try:
                result = record_review_decision(
                    runtime,
                    seed["accepted_review_item_id"],
                    "note_only",
                    None,
                    "operator",
                    False,
                )
                detail = runtime.review_queue.get_review_item(seed["accepted_review_item_id"])
            finally:
                close_local_appliance(runtime)

        self.assertEqual("needs_review", result["review_status"])
        self.assertEqual("needs_review", detail.queue_status.value)

    def test_decision_persists_event_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime, seed = make_runtime(tmp)
            try:
                result = record_review_decision(
                    runtime,
                    seed["accepted_review_item_id"],
                    "accept",
                    None,
                    "operator",
                    True,
                )
                decisions = runtime.review_queue.list_decisions(seed["accepted_review_item_id"])
                events = runtime.review_queue.list_events(seed["accepted_review_item_id"])
            finally:
                close_local_appliance(runtime)

        self.assertTrue(result["review_decision_persisted"])
        self.assertEqual(1, len(decisions))
        self.assertTrue(any(event.event_kind.value == "decision_recorded" for event in events))


if __name__ == "__main__":
    unittest.main()
