from __future__ import annotations

from pathlib import Path
import unittest

from evals.e2e_reference.oracle import (
    DEFAULT_OUTPUT_ROOT,
    OracleError,
    explain_case,
    load_registry,
    run_oracle,
    validate_oracle_run,
    validate_registry,
)
from evals.e2e_reference.oracle.oracle import GATE_FAIL, GATE_WARN, _gate_result


class E2EEvalOracleRegistryTests(unittest.TestCase):
    def test_registry_loads_and_validates(self) -> None:
        registry = load_registry()
        validation = validate_registry(registry)

        self.assertEqual("pass", validation["status"], validation["errors"])
        self.assertEqual(36, validation["case_count"])
        self.assertEqual(7, validation["suite_count"])
        self.assertFalse(validation["model_provider_dependency"])
        self.assertFalse(validation["live_provider_adapter"])

    def test_suites_reference_known_cases_and_baseline_covers_core(self) -> None:
        registry = load_registry()
        case_ids = set(registry.cases)
        baseline_ids = set(registry.baseline["expected_case_ids"])
        core_ids = set(registry.suites["core"]["case_ids"])

        for suite_id, suite in registry.suites.items():
            with self.subTest(suite_id=suite_id):
                self.assertTrue(set(suite["case_ids"]).issubset(case_ids))
        self.assertTrue(core_ids.issubset(baseline_ids))

    def test_critical_cases_have_explicit_prohibited_outcomes(self) -> None:
        registry = load_registry()
        for case_id, case in registry.cases.items():
            with self.subTest(case_id=case_id):
                self.assertIn(case["criticality"], {"critical", "required", "advisory"})
                self.assertTrue(case["proof_levels"])
                if case["criticality"] == "critical":
                    self.assertTrue(case["prohibited_outcomes"])
                self.assertNotIn("live_provider", case["product_adapter"])
                self.assertNotIn("model", case["product_adapter"].casefold())

    def test_unknown_case_fails_clearly(self) -> None:
        with self.assertRaises(OracleError):
            explain_case("missing-case")

    def test_critical_failure_cannot_be_averaged_away(self) -> None:
        self.assertEqual(GATE_FAIL, _gate_result("critical", "not_satisfied", []))
        self.assertEqual(GATE_FAIL, _gate_result("required", "partial", []))
        self.assertEqual(GATE_WARN, _gate_result("advisory", "partial", []))

    def test_case_runs_are_deterministic_but_non_overwriting(self) -> None:
        out_root = Path(DEFAULT_OUTPUT_ROOT) / "test-evals"
        first = run_oracle(case_id="metamorphic_equivalent_blue_ftp", out_root=out_root)
        second = run_oracle(case_id="metamorphic_equivalent_blue_ftp", out_root=out_root)

        self.assertEqual("PASS", first["overall_gate_status"])
        self.assertEqual("PASS", second["overall_gate_status"])
        self.assertNotEqual(first["execution_id"], second["execution_id"])
        self.assertEqual(first["case_summaries"][0]["semantic_hash"], second["case_summaries"][0]["semantic_hash"])
        self.assertEqual(
            "pass",
            validate_oracle_run(Path(DEFAULT_OUTPUT_ROOT) / "test-evals" / first["execution_id"], strict=True)["status"],
        )


if __name__ == "__main__":
    unittest.main()
