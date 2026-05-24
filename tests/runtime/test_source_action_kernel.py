from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.source.action import (
    register_source_action_adapter,
    reset_source_action_registry_for_tests,
    run_source_action,
)


class SourceActionKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_source_action_registry_for_tests()
        register_source_action_adapter(build_adapter())

    def test_fixture_source_action_completes_without_mutation(self) -> None:
        result = run_source_action(query="sampleproject")
        self.assertEqual("completed", result["status"])
        self.assertEqual("fixture_source_action", result["source_family"])
        self.assertFalse(result["live_call_performed"])
        self.assertFalse(result["boundary_report"]["master_index_mutated"])
        self.assertFalse(result["boundary_report"]["operator_instance_mutated"])


if __name__ == "__main__":
    unittest.main()
