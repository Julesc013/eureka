from __future__ import annotations

import unittest

from runtime.public_search import build_public_search_ux_mvp_bundle


class PublicSearchProjectionBoundaryTests(unittest.TestCase):
    def test_projection_boundaries_remain_false(self) -> None:
        bundle = build_public_search_ux_mvp_bundle()

        for key in (
            "deployment_performed",
            "public_launch_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "site_dist_written",
            "public_mutation_enabled",
            "public_live_source_fanout_enabled",
            "download_performed",
            "file_fetch_performed",
            "ocr_performed",
            "extraction_executed",
            "model_provider_used",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "verified_download_claim_created",
            "rights_clearance_claim_created",
        ):
            self.assertFalse(bundle[key], key)


if __name__ == "__main__":
    unittest.main()
