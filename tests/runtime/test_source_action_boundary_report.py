from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.source.action import register_source_action_adapter, reset_source_action_registry_for_tests, run_source_action


class SourceActionBoundaryReportTests(unittest.TestCase):
    def test_boundary_report_keeps_unsafe_flags_false(self) -> None:
        reset_source_action_registry_for_tests()
        register_source_action_adapter(build_adapter())
        report = run_source_action(query="sampleproject")["boundary_report"]
        for field in (
            "live_call_performed",
            "raw_response_committed",
            "source_cache_write_performed",
            "evidence_write_performed",
            "reviewed_index_mutated",
            "master_index_mutated",
            "operator_instance_mutated",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(report[field], field)


if __name__ == "__main__":
    unittest.main()
