from __future__ import annotations

import unittest

from runtime.source.action import check_source_action_policy, default_source_action_policy, plan_source_action


class SourceActionPolicyTests(unittest.TestCase):
    def test_policy_blocks_live_by_default(self) -> None:
        plan = plan_source_action(
            "sampleproject",
            "fixture_source_action",
            "metadata_search",
            default_source_action_policy(),
            transport_mode="operator_approved_live",
        )
        result = check_source_action_policy(plan, default_source_action_policy())
        self.assertFalse(result["allowed"])
        self.assertIn("live_source_calls_disabled_by_default", result["blocked_reasons"])


if __name__ == "__main__":
    unittest.main()
