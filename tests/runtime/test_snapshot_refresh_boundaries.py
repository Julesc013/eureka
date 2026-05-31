from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh


class SnapshotRefreshBoundaryTests(unittest.TestCase):
    def test_boundary_flags_remain_false(self) -> None:
        result = run_snapshot_refresh(from_seed_examples=True)

        for key in (
            "accepted_truth_created",
            "candidate_promoted_to_reviewed",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "site_dist_written",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(result[key], key)


if __name__ == "__main__":
    unittest.main()
