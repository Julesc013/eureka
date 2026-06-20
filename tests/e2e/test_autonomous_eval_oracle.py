from __future__ import annotations

from pathlib import Path
import unittest

from evals.e2e_reference.oracle import DEFAULT_OUTPUT_ROOT, run_oracle, validate_oracle_run


class AutonomousEvalOracleE2ETests(unittest.TestCase):
    def test_core_suite_passes_with_truth_and_public_boundaries(self) -> None:
        summary = run_oracle(suite_id="core", out_root=Path(DEFAULT_OUTPUT_ROOT) / "test-e2e")

        self.assertEqual("PASS", summary["overall_gate_status"])
        self.assertEqual(10, summary["case_count"])
        self.assertEqual(0, summary["critical_failures"])
        self.assertEqual(0, summary["required_failures"])
        self.assertFalse(summary["model_calls"])
        self.assertFalse(summary["network_provider_calls"])
        self.assertFalse(summary["real_truth_mutation"])
        self.assertFalse(summary["public_exposure"])
        self.assertFalse(summary["full_discovery_replacement_claim"])

    def test_all_suite_covers_required_proof_levels_and_resources(self) -> None:
        summary = run_oracle(suite_id="all", out_root=Path(DEFAULT_OUTPUT_ROOT) / "test-e2e")
        validation = validate_oracle_run(Path(DEFAULT_OUTPUT_ROOT) / "test-e2e" / summary["execution_id"], strict=True)

        self.assertEqual("PASS", summary["overall_gate_status"])
        self.assertEqual("pass", validation["status"], validation["errors"])
        self.assertEqual(36, summary["case_count"])
        for proof_level in (
            "shape_proof",
            "semantic_proof",
            "authority_proof",
            "recovery_proof",
            "parity_proof",
            "operational_profile",
        ):
            self.assertGreater(summary["proof_level_counts"].get(proof_level, 0), 0, proof_level)
        self.assertGreater(summary["generated_files"], 0)
        self.assertGreater(summary["generated_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
