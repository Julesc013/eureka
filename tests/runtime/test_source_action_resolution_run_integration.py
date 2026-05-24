from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.source.action import register_source_action_adapter, reset_source_action_registry_for_tests, run_source_action


class SourceActionResolutionRunIntegrationTests(unittest.TestCase):
    def test_source_action_run_has_lane_projection_for_kernel_handoff(self) -> None:
        reset_source_action_registry_for_tests()
        register_source_action_adapter(build_adapter())
        result = run_source_action(query="sampleproject")
        lanes = {lane["lane_kind"] for lane in result["result_lane_projection_plan"]["lanes"]}
        self.assertIn("source_cache_hits", lanes)
        self.assertIn("local_candidate_results", lanes)
        self.assertIn("blocked_actions", lanes)


if __name__ == "__main__":
    unittest.main()
