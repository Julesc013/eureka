import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from scripts.validate_ia_pilot_closeout import (  # noqa: E402
    validate_boundary_matrix,
    validate_closeout_result,
    validate_non_claim_docs,
    validate_stage_results,
)


class IAPilotCloseoutGateTests(unittest.TestCase):
    def test_stage_results_are_present_and_pass(self):
        self.assertEqual([], validate_stage_results(ROOT))

    def test_boundary_matrix_rejects_master_index_mutation(self):
        matrix = json.loads((ROOT / "control/inventory/ia_pilot_boundary_matrix.json").read_text(encoding="utf-8"))
        mutated = copy.deepcopy(matrix)
        mutated["forbidden_boundaries"]["master_index_mutated"] = True
        self.assertIn("forbidden_boundary_not_false:master_index_mutated", validate_boundary_matrix(mutated))

    def test_boundary_matrix_rejects_raw_response_commit(self):
        matrix = json.loads((ROOT / "control/inventory/ia_pilot_boundary_matrix.json").read_text(encoding="utf-8"))
        mutated = copy.deepcopy(matrix)
        mutated["forbidden_boundaries"]["raw_response_committed"] = True
        self.assertIn("forbidden_boundary_not_false:raw_response_committed", validate_boundary_matrix(mutated))

    def test_closeout_result_rejects_production_claim(self):
        result = json.loads((ROOT / "control/inventory/ia_pilot_closeout_result.json").read_text(encoding="utf-8"))
        mutated = copy.deepcopy(result)
        mutated["production_readiness_claimed"] = True
        self.assertIn("closeout_result_expected_false:production_readiness_claimed", validate_closeout_result(mutated))

    def test_docs_state_non_claims(self):
        self.assertEqual([], validate_non_claim_docs(ROOT))


if __name__ == "__main__":
    unittest.main()
