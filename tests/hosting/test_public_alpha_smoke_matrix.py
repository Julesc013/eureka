import json
import unittest
from pathlib import Path

from runtime.hosting.smoke_matrix import REQUIRED_CASE_KINDS, run_local_fixture_smoke_matrix

REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaSmokeMatrixTests(unittest.TestCase):
    def test_smoke_matrix_validates_and_runs_locally(self) -> None:
        matrix = json.loads((REPO_ROOT / "examples/hosting/smoke/public_alpha_smoke_matrix_v0.json").read_text(encoding="utf-8"))
        seen = {case["case_kind"] for case in matrix["smoke_cases"]}
        self.assertEqual(seen, set(REQUIRED_CASE_KINDS))
        result = run_local_fixture_smoke_matrix(matrix, {})
        self.assertEqual(result["status"], "pass", result)
        self.assertFalse(result["external_calls_performed"])


if __name__ == "__main__":
    unittest.main()
