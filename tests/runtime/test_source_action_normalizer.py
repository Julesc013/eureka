from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.source.action import normalize_source_action_result, plan_source_action, run_source_action_fixture


class SourceActionNormalizerTests(unittest.TestCase):
    def test_normalizer_builds_observation_preview(self) -> None:
        adapter = build_adapter()
        plan = plan_source_action("sampleproject", "fixture_source_action", "metadata_search")
        transport = run_source_action_fixture(plan, adapter)
        result = normalize_source_action_result(transport, adapter)
        self.assertEqual(1, result["observation_count"])
        self.assertFalse(result["live_call_performed"])


if __name__ == "__main__":
    unittest.main()
