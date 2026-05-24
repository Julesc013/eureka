from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.source.action import plan_source_action, run_source_action_fixture, update_source_rate_limit_ledger


class SourceActionRateLimitTests(unittest.TestCase):
    def test_rate_limit_ledger_records_fixture_zero_requests(self) -> None:
        plan = plan_source_action("sampleproject", "fixture_source_action", "metadata_search")
        transport = run_source_action_fixture(plan, build_adapter())
        ledger = update_source_rate_limit_ledger(plan, transport)
        self.assertEqual(0, ledger["total_requests"])
        self.assertTrue(ledger["kill_switch_required"])


if __name__ == "__main__":
    unittest.main()
