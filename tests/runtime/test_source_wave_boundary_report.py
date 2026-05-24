from __future__ import annotations

import unittest

from runtime.source.action import REQUIRED_SOURCE_WAVE_FAMILIES, SOURCE_WAVE_FAMILIES, run_source_family_fixture_action


class SourceWaveBoundaryReportTests(unittest.TestCase):
    def test_boundary_report_unsafe_flags_are_false(self) -> None:
        fields = (
            "live_call_performed",
            "raw_response_committed",
            "source_cache_write_performed",
            "evidence_write_performed",
            "candidate_write_performed",
            "reviewed_index_mutated",
            "master_index_mutated",
            "operator_instance_mutated",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        )
        for family in REQUIRED_SOURCE_WAVE_FAMILIES:
            with self.subTest(family=family):
                run = run_source_family_fixture_action(family, SOURCE_WAVE_FAMILIES[family].capabilities[0], "sampleproject")
                for field in fields:
                    self.assertFalse(run["boundary_report"][field], field)


if __name__ == "__main__":
    unittest.main()
