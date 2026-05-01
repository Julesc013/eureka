import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
JOB_CONTRACT = ROOT / "contracts" / "source_sync" / "source_sync_worker_job.v0.json"
MANIFEST_CONTRACT = ROOT / "contracts" / "source_sync" / "source_sync_worker_manifest.v0.json"
KIND_CONTRACT = ROOT / "contracts" / "source_sync" / "source_sync_job_kind.v0.json"
POLICY = ROOT / "control" / "inventory" / "source_sync" / "source_sync_worker_policy.json"
REPORT = ROOT / "control" / "audits" / "source-sync-worker-contract-v0" / "source_sync_worker_contract_report.json"
EXAMPLES = ROOT / "examples" / "source_sync"


class SourceSyncWorkerOperationsTests(unittest.TestCase):
    def test_schema_policy_report_and_examples_exist(self) -> None:
        self.assertTrue(JOB_CONTRACT.is_file())
        self.assertTrue(MANIFEST_CONTRACT.is_file())
        self.assertTrue(KIND_CONTRACT.is_file())
        self.assertTrue(POLICY.is_file())
        self.assertTrue(REPORT.is_file())
        self.assertGreaterEqual(len([path for path in EXAMPLES.iterdir() if path.is_dir()]), 4)
        self.assertEqual(json.loads(JOB_CONTRACT.read_text(encoding="utf-8"))["x-status"], "contract_only")

    def test_policy_hard_flags(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        for key in (
            "runtime_source_sync_implemented",
            "persistent_worker_queue_implemented",
            "telemetry_implemented",
            "credentials_configured",
            "public_query_fanout_allowed",
            "live_source_calls_allowed_now",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "master_index_mutation_allowed",
            "local_index_mutation_allowed",
            "public_index_mutation_allowed",
        ):
            self.assertFalse(policy[key], key)
        for key in (
            "approval_required_for_live_network_sync",
            "operator_required_for_worker_runtime",
            "source_policy_review_required",
            "rate_limit_required_future",
            "timeout_required_future",
            "circuit_breaker_required_future",
            "descriptive_user_agent_required_future",
            "cache_required_before_public_use",
            "evidence_attribution_required",
        ):
            self.assertTrue(policy[key], key)

    def test_example_boundaries(self) -> None:
        for job_path in sorted(EXAMPLES.glob("*/SOURCE_SYNC_WORKER_JOB.json")):
            with self.subTest(path=job_path):
                payload = json.loads(job_path.read_text(encoding="utf-8"))
                self.assertFalse(payload["source_target"]["arbitrary_url_allowed"])
                self.assertFalse(payload["source_policy"]["live_source_enabled_now"])
                for field in (
                    "worker_runtime_implemented",
                    "job_executed",
                    "live_source_called",
                    "external_calls_performed",
                    "telemetry_exported",
                    "credentials_used",
                ):
                    self.assertFalse(payload["no_execution_guarantees"][field], field)
                for field in (
                    "source_cache_mutated",
                    "evidence_ledger_mutated",
                    "candidate_index_mutated",
                    "public_index_mutated",
                    "local_index_mutated",
                    "master_index_mutated",
                    "probe_queue_mutated",
                    "search_need_mutated",
                    "result_cache_mutated",
                ):
                    self.assertFalse(payload["no_mutation_guarantees"][field], field)
                self.assertFalse(payload["rights_and_risk"]["downloads_enabled"])
                self.assertFalse(payload["rights_and_risk"]["installs_enabled"])
                self.assertFalse(payload["rights_and_risk"]["execution_enabled"])

    def test_report_hard_flags(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        for key in (
            "runtime_source_sync_implemented",
            "persistent_worker_queue_implemented",
            "telemetry_implemented",
            "credentials_configured",
            "public_query_fanout_allowed",
            "worker_runtime_implemented",
            "job_executed",
            "live_source_calls_allowed_now",
            "live_source_called",
            "external_calls_performed",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "master_index_mutation_allowed",
            "local_index_mutation_allowed",
            "public_index_mutation_allowed",
        ):
            self.assertFalse(report[key], key)

    def test_docs_state_contract_only_no_runtime_no_mutation(self) -> None:
        text = (ROOT / "docs" / "reference" / "SOURCE_SYNC_WORKER_CONTRACT.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "not connector runtime yet",
            "not a crawler/scraper",
            "not public-query fanout",
            "not source cache/evidence ledger mutation in v0",
            "live source sync requires approval",
            "cache-first",
            "evidence attribution",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
