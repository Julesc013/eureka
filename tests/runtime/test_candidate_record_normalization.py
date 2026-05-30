from __future__ import annotations

import unittest

from runtime.candidate_store import archive_org_candidate_to_record, sample_archive_org_candidate
from runtime.search.query_plan import plan_query_to_source_actions


class CandidateRecordNormalizationTest(unittest.TestCase):
    def test_archive_candidate_normalizes_required_fields(self) -> None:
        plan = plan_query_to_source_actions("StyleWriter 2500 Mac OS 8 driver")
        candidate = archive_org_candidate_to_record(sample_archive_org_candidate("StyleWriter 2500 Mac OS 8 driver"), plan)

        for field in (
            "candidate_id",
            "candidate_kind",
            "source_family",
            "source_locator",
            "title",
            "description",
            "matched_query",
            "query_plan_ref",
            "source_action_ref",
            "source_observation_ref",
            "evidence_candidate_refs",
            "domain_id",
            "confidence_label",
            "match_reasons",
            "suppressions",
            "limitations",
            "action_posture",
            "review_state",
            "accepted_truth",
            "reviewed_record_ref",
            "created_at",
            "updated_at",
        ):
            self.assertIn(field, candidate)
        self.assertFalse(candidate["accepted_truth"])
        self.assertIsNone(candidate["reviewed_record_ref"])
        self.assertEqual(candidate["review_state"], "needs_review")


if __name__ == "__main__":
    unittest.main()
