from __future__ import annotations

import unittest

from runtime.source_observation.ia_live_metadata_lane import build_ia_live_metadata_lane_boundary_report, run_ia_live_metadata_lane_mock


class IALiveMetadataLaneBoundariesTests(unittest.TestCase):
    def test_mock_live_boundary_has_no_side_effects(self) -> None:
        result = run_ia_live_metadata_lane_mock("run-test", "sampleproject")
        boundary = build_ia_live_metadata_lane_boundary_report("run-test", result)
        for key in (
            "raw_response_committed",
            "download_performed",
            "upload_performed",
            "extraction_executed",
            "operator_instance_mutated",
            "master_index_mutated",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "full_archive_org_integration_claimed",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
