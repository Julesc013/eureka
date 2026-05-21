import unittest

from runtime.local_eval.g0_quality import build_user_cost_score, load_quality_fixture


class G0UserCostTests(unittest.TestCase):
    def test_user_cost_scores_block_unsafe_actions(self) -> None:
        fixture = load_quality_fixture("examples/search_quality/sample_quality_fixture.json")
        scores = [build_user_cost_score(record, fixture["action_posture"]) for record in fixture["records"]]
        classes = {score["user_cost_class"] for score in scores}
        self.assertIn("direct_reviewed_result", classes)
        self.assertIn("source_cache_hit_needs_evidence", classes)
        self.assertIn("member_path_known", classes)
        for score in scores:
            self.assertFalse(score["accepted_truth"])
            self.assertIn("download", score["blocked_actions"])
            self.assertIn("call_model_provider", score["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
