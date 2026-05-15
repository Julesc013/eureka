import unittest
from pathlib import Path

from scripts.prepare_hunt_to_main_promotion_review import prepare_review


class HuntToMainPromotionReviewTests(unittest.TestCase):
    def test_promotion_review_is_plan_only(self):
        result = prepare_review(Path.cwd())
        self.assertEqual(result["promotion_task"], "HUNT-TO-MAIN-PROMOTION-REVIEW")
        self.assertFalse(result["branch_mutation_performed"])
        self.assertFalse(result["merge_performed"])
        self.assertFalse(result["push_performed"])
        self.assertTrue(result["no_deployment"])
        self.assertTrue(result["no_production_readiness_claim"])
        self.assertTrue(result["no_public_launch_readiness_claim"])


if __name__ == "__main__":
    unittest.main()
