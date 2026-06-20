from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "e2e_reference_system" / "live_product_hardening_audit_v1"


class LiveProductHardeningAuditTests(unittest.TestCase):
    def test_required_audit_artifacts_exist(self) -> None:
        expected = {
            "README.md",
            "AUDIT_REPORT.md",
            "findings.json",
            "security_matrix.json",
            "recovery_matrix.json",
            "performance_baseline.json",
            "provider_policy_matrix.json",
            "portability_matrix.json",
            "remaining_risks.md",
        }

        self.assertEqual(expected, {path.name for path in AUDIT.iterdir()})

    def test_findings_have_no_critical_or_high_and_keep_external_gates_open(self) -> None:
        payload = json.loads((AUDIT / "findings.json").read_text(encoding="utf-8"))

        self.assertEqual("pass_with_warnings", payload["status"])
        self.assertEqual(0, payload["critical_count"])
        self.assertEqual(0, payload["high_count"])
        self.assertEqual(3, payload["medium_count"])
        medium_titles = {
            finding["title"]
            for finding in payload["findings"]
            if finding["severity"] == "medium"
        }
        self.assertIn("Operator real live canary has not run in this session", medium_titles)
        self.assertIn("Human product acceptance has not started", medium_titles)
        self.assertIn("Full unittest discovery is waiting for external execution", medium_titles)
        self.assertTrue(payload["blocks_agentic_planner"])

    def test_security_matrix_preserves_no_persistence_and_no_public_mutation(self) -> None:
        payload = json.loads((AUDIT / "security_matrix.json").read_text(encoding="utf-8"))

        self.assertFalse(payload["public_exposure_enabled"])
        self.assertFalse(payload["public_live_fanout_enabled"])
        self.assertFalse(payload["reviewed_master_mutation"])
        self.assertFalse(payload["public_index_mutation"])
        self.assertFalse(payload["provider_result_payload_persisted"])
        self.assertFalse(payload["model_or_agent_calls"])

    def test_performance_baseline_is_deterministic_and_non_production_claiming(self) -> None:
        payload = json.loads((AUDIT / "performance_baseline.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual([10, 25], payload["dataset_sizes"])
        self.assertFalse(payload["production_scale_claimed"])
        self.assertFalse(payload["network_provider_calls"])
        self.assertFalse(payload["model_provider_calls"])
        for dataset in payload["datasets"]:
            self.assertIn("p50", dataset["fts_query_latency_ms"])
            self.assertIn("p95", dataset["fts_query_latency_ms"])
            self.assertIn("p99", dataset["fts_query_latency_ms"])

    def test_provider_and_portability_matrices_keep_live_gates_honest(self) -> None:
        provider = json.loads((AUDIT / "provider_policy_matrix.json").read_text(encoding="utf-8"))
        portability = json.loads((AUDIT / "portability_matrix.json").read_text(encoding="utf-8"))

        brave = next(item for item in provider["providers"] if item["provider_id"] == "brave_web_search")
        self.assertFalse(brave["retention"]["persist_urls"])
        self.assertFalse(brave["retention"]["persist_snippets"])
        self.assertFalse(brave["retention"]["persist_rank"])
        self.assertEqual("waiting_for_operator_live_canary", brave["live_canary_state"])
        self.assertEqual("pass_with_warnings", portability["status"])
        self.assertTrue(any("local source-checkout" in item for item in portability["limitations"]))


if __name__ == "__main__":
    unittest.main()
