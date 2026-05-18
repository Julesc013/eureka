import unittest

from runtime.source_observation.internet_archive_promotion import (
    build_ia_promotion_boundary_report,
    build_ia_promotion_dry_run_report,
    load_ia_promotion_dry_run_policy,
)
from runtime.source_observation.internet_archive_review import build_ia_review_boundary_report, build_ia_review_queue_report


class IAPromotionBoundaryTests(unittest.TestCase):
    def test_review_boundary_keeps_reviewed_and_master_mutations_false(self):
        report = build_ia_review_queue_report(
            [],
            [],
            dry_run=True,
            store_result={"write_applied": False},
            write_scope="dry_run_no_instance_mutation",
        )
        boundary = build_ia_review_boundary_report(report)
        self.assertTrue(boundary["passed"])
        self.assertFalse(boundary["accepted_truth_created"])
        self.assertFalse(boundary["reviewed_index_mutated"])
        self.assertFalse(boundary["master_index_mutated"])

    def test_promotion_boundary_keeps_preview_only(self):
        policy = load_ia_promotion_dry_run_policy()
        report = build_ia_promotion_dry_run_report([], policy)
        boundary = build_ia_promotion_boundary_report(report)
        self.assertTrue(boundary["passed"])
        self.assertTrue(boundary["all_promotion_previews_preview_only"])
        self.assertFalse(boundary["accepted_truth_created"])
        self.assertFalse(boundary["reviewed_index_mutated"])
        self.assertFalse(boundary["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
