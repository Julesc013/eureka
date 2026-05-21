import unittest

from runtime.local_eval.g0_quality import build_identity_cluster_candidates, build_near_miss_candidates, load_quality_fixture


class G0IdentityClusterTests(unittest.TestCase):
    def test_identity_clusters_are_provisional(self) -> None:
        fixture = load_quality_fixture("examples/search_quality/sample_quality_fixture.json")
        clusters = build_identity_cluster_candidates(fixture["records"])
        self.assertGreaterEqual(len(clusters["identity_cluster_candidates"]), 1)
        for cluster in clusters["identity_cluster_candidates"]:
            self.assertTrue(cluster["provisional"])
            self.assertFalse(cluster["accepted_identity_merge"])
            self.assertFalse(cluster["accepted_truth"])

    def test_near_misses_explain_mismatch(self) -> None:
        fixture = load_quality_fixture("examples/search_quality/sample_quality_fixture.json")
        near = build_near_miss_candidates(fixture["records"], fixture["query_context"])
        self.assertGreaterEqual(len(near["near_miss_candidates"]), 1)
        reasons = {reason for candidate in near["near_miss_candidates"] for reason in candidate["mismatch_reasons"]}
        self.assertIn("wrong_platform_candidate", reasons)


if __name__ == "__main__":
    unittest.main()
