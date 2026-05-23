from __future__ import annotations

import unittest

from runtime.local.service.workbench_review_promote import run_review_promote_flow


class WorkbenchReviewBoundariesTests(unittest.TestCase):
    def test_public_and_native_projections_are_read_only(self) -> None:
        for projection, key in (
            ("public_web", "public_projection_blocked"),
            ("native_desktop_read_only", "native_read_only_projection_blocked"),
        ):
            result = run_review_promote_flow(projection_profile=projection, dry_run=True)
            self.assertTrue(result[key], result)
            self.assertFalse(result["review_decision"]["allowed"], result)
            self.assertFalse(result["promotion_preview_created"], result)

    def test_boundary_flags_remain_false(self) -> None:
        result = run_review_promote_flow(dry_run=True)
        for key in (
            "automatic_candidate_acceptance_enabled",
            "fake_evidence_created",
            "fake_verified_records_created",
            "operator_instance_mutated",
            "master_index_mutated",
            "committed_data_public_index_mutated",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
        ):
            self.assertFalse(result[key], key)


if __name__ == "__main__":
    unittest.main()
