import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_POLICY = ROOT / "control" / "inventory" / "source_cache" / "source_cache_policy.json"
LEDGER_POLICY = ROOT / "control" / "inventory" / "evidence_ledger" / "evidence_ledger_policy.json"
REPORT = ROOT / "control" / "audits" / "source-cache-evidence-ledger-v0" / "source_cache_evidence_ledger_report.json"


class SourceCacheEvidenceLedgerOperationsTests(unittest.TestCase):
    def test_contracts_examples_and_report_exist(self) -> None:
        for path in (
            ROOT / "contracts/source_cache/source_cache_record.v0.json",
            ROOT / "contracts/source_cache/source_cache_manifest.v0.json",
            ROOT / "contracts/evidence_ledger/evidence_ledger_record.v0.json",
            ROOT / "contracts/evidence_ledger/evidence_ledger_manifest.v0.json",
            SOURCE_POLICY,
            LEDGER_POLICY,
            REPORT,
        ):
            self.assertTrue(path.is_file(), path)
        self.assertEqual(len(list((ROOT / "examples/source_cache").glob("*/SOURCE_CACHE_RECORD.json"))), 3)
        self.assertEqual(len(list((ROOT / "examples/evidence_ledger").glob("*/EVIDENCE_LEDGER_RECORD.json"))), 3)

    def test_policy_hard_flags(self) -> None:
        source_policy = json.loads(SOURCE_POLICY.read_text(encoding="utf-8"))
        ledger_policy = json.loads(LEDGER_POLICY.read_text(encoding="utf-8"))
        for key in (
            "runtime_source_cache_implemented",
            "persistent_source_cache_implemented",
            "live_sources_enabled_by_default",
            "public_query_fanout_allowed",
            "arbitrary_url_cache_allowed",
            "raw_payload_storage_allowed_now",
            "private_data_storage_allowed_now",
            "executable_payload_storage_allowed_now",
            "telemetry_implemented",
            "credentials_configured",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "master_index_mutation_allowed",
        ):
            self.assertFalse(source_policy[key], key)
        for key in (
            "runtime_evidence_ledger_implemented",
            "persistent_evidence_ledger_implemented",
            "accepted_as_truth_by_default",
            "automatic_promotion_allowed",
            "telemetry_implemented",
            "credentials_configured",
            "ledger_mutation_allowed_now",
            "source_cache_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "public_index_mutation_allowed_now",
            "local_index_mutation_allowed_now",
            "master_index_mutation_allowed",
            "destructive_merge_allowed",
        ):
            self.assertFalse(ledger_policy[key], key)

    def test_report_hard_flags(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        for key in (
            "runtime_source_cache_implemented",
            "persistent_source_cache_implemented",
            "runtime_evidence_ledger_implemented",
            "persistent_evidence_ledger_implemented",
            "source_cache_runtime_implemented",
            "evidence_ledger_runtime_implemented",
            "cache_write_performed",
            "ledger_write_performed",
            "live_sources_enabled_by_default",
            "public_query_fanout_allowed",
            "arbitrary_url_cache_allowed",
            "raw_payload_storage_allowed_now",
            "private_data_storage_allowed_now",
            "executable_payload_storage_allowed_now",
            "accepted_as_truth_by_default",
            "automatic_promotion_allowed",
            "live_source_called",
            "external_calls_performed",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "public_index_mutation_allowed_now",
            "local_index_mutation_allowed_now",
            "master_index_mutation_allowed",
            "telemetry_implemented",
            "credentials_configured",
        ):
            self.assertFalse(report[key], key)

    def test_docs_state_contract_only_no_runtime_no_truth(self) -> None:
        source_text = (ROOT / "docs/reference/SOURCE_CACHE_CONTRACT.md").read_text(encoding="utf-8").casefold()
        ledger_text = (ROOT / "docs/reference/EVIDENCE_LEDGER_CONTRACT.md").read_text(encoding="utf-8").casefold()
        for phrase in ("not live connector runtime", "not arbitrary url cache", "not a raw payload store", "runtime source cache is contract-only"):
            self.assertIn(phrase, source_text)
        for phrase in ("not truth by default", "accepted_as_truth is false", "confidence is not truth", "master-index review"):
            self.assertIn(phrase, ledger_text)


if __name__ == "__main__":
    unittest.main()
