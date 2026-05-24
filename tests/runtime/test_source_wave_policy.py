from __future__ import annotations

import unittest

from runtime.source.action import (
    check_source_action_policy,
    default_source_action_policy,
    plan_source_action,
)


class SourceWavePolicyTests(unittest.TestCase):
    def test_live_transport_is_blocked_by_default(self) -> None:
        plan = plan_source_action(
            "sampleproject",
            "github_releases_metadata",
            "release_metadata_read",
            default_source_action_policy(),
            transport_mode="operator_approved_live",
        )
        result = check_source_action_policy(plan, default_source_action_policy())
        self.assertFalse(result["allowed"])
        self.assertIn("live_source_calls_disabled_by_default", result["blocked_reasons"])


if __name__ == "__main__":
    unittest.main()
