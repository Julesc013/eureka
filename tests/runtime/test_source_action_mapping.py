from __future__ import annotations

import unittest

from runtime.connectors.fixture_source_action import build_adapter
from runtime.source.action import (
    build_candidate_mapping_plan,
    build_evidence_candidate_mapping_plan,
    build_source_cache_mapping_plan,
    build_source_observation_envelope,
    normalize_source_action_result,
    plan_source_action,
    run_source_action_fixture,
)


class SourceActionMappingTests(unittest.TestCase):
    def test_mapping_plans_do_not_mutate_stores(self) -> None:
        adapter = build_adapter()
        plan = plan_source_action("sampleproject", "fixture_source_action", "metadata_search")
        transport = run_source_action_fixture(plan, adapter)
        normalized = normalize_source_action_result(transport, adapter)
        observation = build_source_observation_envelope(normalized)
        plans = [
            build_source_cache_mapping_plan(observation),
            build_evidence_candidate_mapping_plan(observation),
            build_candidate_mapping_plan(observation),
        ]
        for mapping in plans:
            self.assertFalse(mapping["write_performed"])
            self.assertFalse(mapping["store_mutation_performed"])


if __name__ == "__main__":
    unittest.main()
