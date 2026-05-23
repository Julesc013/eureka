from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_observation_candidate import (
    CANDIDATE_EXAMPLES,
    REVIEW_EXAMPLES,
    validate_candidate_record,
    validate_observation_candidates,
    validate_review_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class ObservationCandidateContractsTest(unittest.TestCase):
    def test_valid_observation_candidate_examples_pass(self) -> None:
        for path in CANDIDATE_EXAMPLES:
            with self.subTest(path=path):
                payload = _read_json(REPO_ROOT / path)
                self.assertEqual(validate_candidate_record(payload, path), [])

    def test_valid_review_examples_pass(self) -> None:
        for path in REVIEW_EXAMPLES:
            with self.subTest(path=path):
                payload = _read_json(REPO_ROOT / path)
                self.assertEqual(validate_review_record(payload, path), [])

    def test_current_repo_candidates_validate(self) -> None:
        report = validate_observation_candidates(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_candidate_accepted_as_observed_baseline_fails(self) -> None:
        candidate = _candidate()
        candidate["accepted_as_observed_baseline"] = True

        errors = validate_candidate_record(candidate, "broken_candidate")

        self.assertTrue(any("accepted_as_observed_baseline" in error for error in errors))

    def test_candidate_accepted_as_evidence_truth_fails(self) -> None:
        candidate = _candidate()
        candidate["accepted_as_evidence_truth"] = True

        errors = validate_candidate_record(candidate, "broken_candidate")

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))

    def test_candidate_master_index_mutation_fails(self) -> None:
        candidate = _candidate()
        candidate["master_index_mutation_allowed"] = True

        errors = validate_candidate_record(candidate, "broken_candidate")

        self.assertTrue(any("master_index_mutation_allowed" in error for error in errors))

    def test_unapproved_live_source_candidate_fails(self) -> None:
        candidate = _candidate()
        candidate["source_access_mode"] = "approved_api_future"
        candidate["source_policy_status"] = "active_current_access"

        errors = validate_candidate_record(candidate, "broken_candidate")

        self.assertTrue(any("future source access" in error for error in errors))

    def test_google_scrape_candidate_fails(self) -> None:
        candidate = _candidate()
        candidate["candidate_summary"] = "This candidate uses scraped Google result text."

        errors = validate_candidate_record(candidate, "broken_candidate")

        self.assertTrue(any("forbidden claim marker" in error for error in errors))

    def test_ai_summary_as_evidence_truth_fails(self) -> None:
        candidate = _candidate()
        candidate["origin"] = "ai_summary_future"
        candidate["accepted_as_evidence_truth"] = True

        errors = validate_candidate_record(candidate, "broken_candidate")

        self.assertTrue(any("accepted_as_evidence_truth" in error or "AI summary" in error for error in errors))

    def test_source_lead_as_observed_baseline_fails(self) -> None:
        candidate = _candidate()
        candidate["candidate_type"] = "source_lead"
        candidate["accepted_as_observed_baseline"] = True

        errors = validate_candidate_record(candidate, "broken_candidate")

        self.assertTrue(any("accepted_as_observed_baseline" in error for error in errors))

    def test_review_decision_accepting_truth_fails(self) -> None:
        review = _read_json(REPO_ROOT / "examples/review/observation_reviews/approve_observation_candidate_review_v0.json")
        broken = deepcopy(review)
        broken["accepted_as_evidence_truth"] = True
        broken["master_index_mutation_allowed"] = True

        errors = validate_review_record(broken, "broken_review")

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))
        self.assertTrue(any("master_index_mutation_allowed" in error for error in errors))

    def test_single_file_validation_reports_invalid(self) -> None:
        candidate = _candidate()
        candidate["accepted_as_observed_baseline"] = True
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "candidate.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            errors = validate_candidate_record(_read_json(path), str(path))

        self.assertTrue(errors)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/observation_candidates/minimal_observation_candidate_v0.json"))


if __name__ == "__main__":
    unittest.main()
