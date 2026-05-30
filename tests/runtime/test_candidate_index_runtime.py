from __future__ import annotations

import unittest

from runtime.candidate_store import (
    apply_candidate_index_write_plan_temp,
    archive_org_candidate_to_record,
    build_candidate_index_write_plan,
    sample_archive_org_candidate,
)
from runtime.search.query_plan import plan_query_to_source_actions


class CandidateIndexRuntimeTest(unittest.TestCase):
    def test_temp_write_plan_applies_without_index_mutation_flags(self) -> None:
        plan = plan_query_to_source_actions("New York 1993 D-Theater HD demo tape original source")
        candidate = archive_org_candidate_to_record(sample_archive_org_candidate(), plan)
        write_plan = build_candidate_index_write_plan(candidate, "temp_store")
        store: dict[str, object] = {}

        result = apply_candidate_index_write_plan_temp(write_plan, store)

        self.assertTrue(result["write_applied"])
        self.assertEqual(result["candidate_count"], 1)
        self.assertFalse(result["accepted_truth_created"])
        self.assertFalse(result["reviewed_index_mutated"])
        self.assertFalse(result["master_index_mutated"])
        self.assertFalse(result["public_index_mutated"])
        self.assertFalse(result["operator_instance_mutated"])


if __name__ == "__main__":
    unittest.main()
