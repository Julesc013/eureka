from __future__ import annotations

import unittest

from runtime.review.batch import build_candidate_clusters, load_review_batch_inputs_from_examples


class ReviewBatchClusteringTests(unittest.TestCase):
    def test_clusters_include_scout_and_review_priority_groups(self) -> None:
        inputs = load_review_batch_inputs_from_examples()
        clusters = build_candidate_clusters(inputs["candidates"], inputs["scout_relations"])
        kinds = {cluster["cluster_kind"] for cluster in clusters}
        self.assertIn("same_source_family_cluster", kinds)
        self.assertIn("review_priority_cluster", kinds)
        self.assertTrue(all(cluster["accepted_truth"] is False for cluster in clusters))


if __name__ == "__main__":
    unittest.main()
