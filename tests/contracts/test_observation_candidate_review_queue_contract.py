from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.validate_observation_candidate_review_queue import (
    EXAMPLE_PATHS,
    validate_contract_payload,
    validate_queue_entry,
    validate_queue_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class ObservationCandidateReviewQueueContractTest(unittest.TestCase):
    def test_contract_json_is_valid_and_declares_boundaries(self) -> None:
        payload = _read_json(REPO_ROOT / "control/schemas/tasks/query/observation_candidate_review_queue.v0.json")

        errors = validate_contract_payload(payload, "contract")

        self.assertEqual(errors, [])
        self.assertFalse(payload["x-master-index-mutation-allowed"])
        self.assertFalse(payload["x-source-access-approved"])

    def test_review_queue_examples_validate(self) -> None:
        for path in EXAMPLE_PATHS:
            with self.subTest(path=path):
                payload = _read_json(REPO_ROOT / path)
                self.assertEqual(validate_queue_payload(payload, path, REPO_ROOT), [])

    def test_queue_entry_requires_human_review(self) -> None:
        entry = _entry()
        entry["review_required"] = False

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("review_required" in error for error in errors))

    def test_queue_entry_truth_boundaries_fail_when_true(self) -> None:
        for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
            with self.subTest(field=field):
                entry = _entry()
                entry[field] = True

                errors = validate_queue_entry(entry, "broken", REPO_ROOT)

                self.assertTrue(any(field in error for error in errors))

    def test_review_decision_ref_must_remain_null(self) -> None:
        entry = _entry()
        entry["review_decision_ref"] = "examples/observation_reviews/approve_observation_candidate_review_v0.json"

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("review_decision_ref" in error for error in errors))

    def test_recommended_action_must_be_future_vocabulary(self) -> None:
        entry = _entry()
        entry["recommended_review_action"] = "approve_now"

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("recommended_review_action" in error for error in errors))


def _entry() -> dict:
    queue = _read_json(REPO_ROOT / "examples/observation_reviews/review_queue_minimal_v0.json")
    return deepcopy(queue["queue_entries"][0])


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
