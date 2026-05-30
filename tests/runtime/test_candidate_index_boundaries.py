from __future__ import annotations

import unittest

from runtime.candidate_store import build_candidate_boundary_report


class CandidateIndexBoundariesTest(unittest.TestCase):
    def test_boundary_report_keeps_forbidden_actions_false(self) -> None:
        report = build_candidate_boundary_report("unit_test")
        for key in (
            "accepted_truth_created",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_mutation_enabled",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(report[key], key)


if __name__ == "__main__":
    unittest.main()
