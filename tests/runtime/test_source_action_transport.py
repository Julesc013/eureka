from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.source.action import plan_source_action, run_source_action_fixture


class SourceActionTransportTests(unittest.TestCase):
    def test_fixture_transport_has_no_remote_requests(self) -> None:
        plan = plan_source_action("sampleproject", "fixture_source_action", "metadata_search")
        result = run_source_action_fixture(plan, build_adapter())
        self.assertEqual("completed", result["status"])
        self.assertEqual(0, result["total_requests"])
        self.assertFalse(result["raw_response_persisted"])


if __name__ == "__main__":
    unittest.main()
