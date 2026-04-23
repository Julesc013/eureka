from __future__ import annotations

import unittest

from runtime.engine.strategy import (
    bootstrap_strategy_profile_ids,
    resolve_bootstrap_strategy_profile,
)


class StrategyProfileTestCase(unittest.TestCase):
    def test_bootstrap_strategy_profiles_include_expected_fixed_ids(self) -> None:
        self.assertEqual(
            bootstrap_strategy_profile_ids(),
            ("inspect", "preserve", "acquire", "compare"),
        )

    def test_missing_strategy_defaults_to_inspect(self) -> None:
        profile = resolve_bootstrap_strategy_profile(None)

        self.assertEqual(profile.strategy_id, "inspect")
        self.assertIn("prioritize_source_inspection", profile.emphasis_hints)

    def test_unknown_strategy_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            resolve_bootstrap_strategy_profile("unknown-strategy")
