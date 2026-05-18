import unittest
from pathlib import Path

from runtime.source_observation.internet_archive_review import (
    apply_ia_review_decision,
    build_ia_review_items_from_candidates,
    load_default_ia_candidate_records,
    load_ia_review_policy,
    to_review_decision_record,
    validate_ia_review_decision,
    validate_ia_review_item,
)


ROOT = Path(__file__).resolve().parents[2]


class IAReviewDecisionTests(unittest.TestCase):
    def test_review_items_from_fixture_and_live_candidates_validate(self):
        policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        items = build_ia_review_items_from_candidates(load_default_ia_candidate_records(), policy)
        self.assertTrue(items)
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_fixture_replay" for item in items))
        self.assertTrue(any(item["provenance"]["source_kind"] == "ia_live_probe_preview" for item in items))
        self.assertTrue(all(validate_ia_review_item(item, policy) == () for item in items))

    def test_all_allowed_decisions_preserve_boundaries(self):
        policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        item = build_ia_review_items_from_candidates(load_default_ia_candidate_records()[:1], policy)[0]
        for decision_name in policy["allowed_decisions"]:
            decision = apply_ia_review_decision(item, decision_name, policy)
            self.assertEqual((), validate_ia_review_decision(decision, policy), decision_name)
            self.assertFalse(decision["accepted_truth"])
            self.assertFalse(decision["reviewed_index_mutation_performed"])
            self.assertFalse(decision["master_index_mutation_performed"])

    def test_approve_decision_creates_preview_only_signal(self):
        policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        item = build_ia_review_items_from_candidates(load_default_ia_candidate_records()[:1], policy)[0]
        decision = apply_ia_review_decision(item, "approve_for_reviewed_index_dry_run", policy)
        self.assertTrue(decision["creates_promotion_preview"])
        durable = to_review_decision_record(decision)
        self.assertEqual("accept", durable.decision_kind.value)
        self.assertNotIn("accepted_truth", str(durable.payload))


if __name__ == "__main__":
    unittest.main()
