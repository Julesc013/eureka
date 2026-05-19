import unittest
from pathlib import Path

from runtime.source_observation.internet_archive_promotion import (
    build_ia_promotion_preview,
    build_ia_promotion_previews,
    load_ia_promotion_dry_run_policy,
    validate_ia_promotion_preview,
)
from runtime.source_observation.internet_archive_review import (
    apply_ia_review_decision,
    build_ia_review_items_from_candidates,
    load_default_ia_candidate_records,
    load_ia_review_policy,
)


ROOT = Path(__file__).resolve().parents[2]


class IAPromotionDryRunTests(unittest.TestCase):
    def test_approve_decision_creates_dry_run_record(self):
        review_policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        promotion_policy = load_ia_promotion_dry_run_policy(ROOT / "control/policies/ia_promotion_dry_run_policy.json")
        item = build_ia_review_items_from_candidates(load_default_ia_candidate_records()[:1], review_policy)[0]
        decision = apply_ia_review_decision(item, "approve_for_reviewed_index_dry_run", review_policy)
        preview = build_ia_promotion_preview(decision, None, promotion_policy)
        self.assertIsNotNone(preview)
        self.assertTrue(preview["promotion_dry_run_only"])
        self.assertFalse(preview["reviewed_index_write_performed"])
        self.assertFalse(preview["master_index_write_performed"])
        self.assertEqual((), validate_ia_promotion_preview(preview, promotion_policy))

    def test_non_approve_decision_creates_no_preview(self):
        review_policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        promotion_policy = load_ia_promotion_dry_run_policy(ROOT / "control/policies/ia_promotion_dry_run_policy.json")
        item = build_ia_review_items_from_candidates(load_default_ia_candidate_records()[:1], review_policy)[0]
        decision = apply_ia_review_decision(item, "needs_more_evidence", review_policy)
        self.assertIsNone(build_ia_promotion_preview(decision, None, promotion_policy))

    def test_promotion_previews_preserve_provenance_uncertainty_and_limitations(self):
        review_policy = load_ia_review_policy(ROOT / "control/policies/ia_review_policy.json")
        promotion_policy = load_ia_promotion_dry_run_policy(ROOT / "control/policies/ia_promotion_dry_run_policy.json")
        items = build_ia_review_items_from_candidates(load_default_ia_candidate_records()[:3], review_policy)
        decisions = [apply_ia_review_decision(item, "approve_for_reviewed_index_dry_run", review_policy) for item in items]
        previews = build_ia_promotion_previews(decisions, promotion_policy)
        self.assertEqual(len(items), len(previews))
        self.assertTrue(all(preview["provenance"] for preview in previews))
        self.assertTrue(all(preview["uncertainty"] for preview in previews))
        self.assertTrue(all(preview["limitations"] for preview in previews))


if __name__ == "__main__":
    unittest.main()
