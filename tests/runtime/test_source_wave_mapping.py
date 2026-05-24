from __future__ import annotations

import unittest

from runtime.source.action import REQUIRED_SOURCE_WAVE_FAMILIES, SOURCE_WAVE_FAMILIES, run_source_family_fixture_action


class SourceWaveMappingTests(unittest.TestCase):
    def test_mapping_plans_do_not_mutate_stores(self) -> None:
        for family in REQUIRED_SOURCE_WAVE_FAMILIES:
            with self.subTest(family=family):
                action_kind = SOURCE_WAVE_FAMILIES[family].capabilities[0]
                run = run_source_family_fixture_action(family, action_kind, "sampleproject")
                for key in ("source_cache_mapping_plan", "evidence_candidate_mapping_plan", "candidate_mapping_plan"):
                    self.assertFalse(run[key]["store_mutation_performed"])
                    self.assertFalse(run[key]["write_performed"])


if __name__ == "__main__":
    unittest.main()
