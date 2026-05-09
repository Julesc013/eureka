import json
import unittest
from pathlib import Path

from runtime.local_foundry import source_cache


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_example(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples/source_cache_records" / name).read_text(encoding="utf-8"))


class LocalSourceCacheRuntimeTests(unittest.TestCase):
    def test_build_source_cache_record_works_on_source_lead_example(self) -> None:
        record = source_cache.build_source_cache_record(load_example("source_lead_record_v0.json"))
        self.assertEqual(record["source_cache_record_type"], "source_lead_record")
        self.assertEqual(record["source_cache_record_status"], "candidate_source_record")
        self.assertFalse(record["truth_boundary"]["source_cache_record_is_public_truth"])
        self.assertFalse(record["truth_boundary"]["source_cache_record_is_accepted_evidence"])

    def test_source_metadata_record_classifies_correctly(self) -> None:
        record = source_cache.build_source_cache_record(load_example("source_metadata_record_v0.json"))
        self.assertEqual(source_cache.classify_source_cache_record_type(record), "source_metadata")

    def test_source_locator_record_classifies_correctly(self) -> None:
        record = source_cache.build_source_cache_record(load_example("source_locator_record_v0.json"))
        self.assertEqual(source_cache.classify_source_cache_record_type(record), "source_locator")

    def test_source_policy_record_classifies_correctly(self) -> None:
        record = source_cache.build_source_cache_record(load_example("source_policy_record_v0.json"))
        self.assertEqual(source_cache.classify_source_cache_record_type(record), "source_policy_record")

    def test_source_coverage_record_classifies_correctly(self) -> None:
        record = source_cache.build_source_cache_record(load_example("source_coverage_record_v0.json"))
        self.assertEqual(source_cache.classify_source_cache_record_type(record), "source_coverage_record")

    def test_connector_fixture_record_remains_fixture_only(self) -> None:
        record = source_cache.build_source_cache_record(load_example("connector_fixture_record_v0.json"))
        self.assertEqual(record["source_cache_record_type"], "connector_fixture_record")
        self.assertEqual(record["source_cache_record_status"], "fixture_only")

    def test_policy_blocked_source_cache_record_remains_policy_blocked(self) -> None:
        record = source_cache.build_source_cache_record(load_example("policy_blocked_source_cache_record_v0.json"))
        self.assertEqual(record["source_cache_record_status"], "policy_blocked")

    def test_source_access_violation_is_flagged(self) -> None:
        record = source_cache.build_source_cache_record({"source_label": "Synthetic", "source_access_mode": "live_probe"})
        errors = source_cache.validate_source_cache_record(record)
        self.assertTrue(any("source_access_mode" in error for error in errors), errors)
        record = source_cache.build_source_cache_record({"source_label": "Synthetic", "source_locator": "https://example.invalid/source"})
        errors = source_cache.validate_source_cache_record(record)
        self.assertTrue(any("live URL" in error for error in errors), errors)

    def test_truth_boundary_violation_is_rejected(self) -> None:
        record = source_cache.build_source_cache_record(load_example("minimal_source_cache_record_v0.json"))
        record["truth_boundary"]["source_cache_record_is_public_truth"] = True
        self.assertTrue(source_cache.detect_truth_boundary_violations(record))
        self.assertTrue(source_cache.validate_source_cache_record(record))

    def test_accepted_evidence_claim_is_rejected(self) -> None:
        record = source_cache.build_source_cache_record(load_example("minimal_source_cache_record_v0.json"))
        record["truth_boundary"]["source_cache_record_is_accepted_evidence"] = True
        errors = source_cache.validate_source_cache_record(record)
        self.assertTrue(any("accepted_evidence" in error for error in errors), errors)

    def test_master_index_mutation_claim_is_rejected(self) -> None:
        record = source_cache.build_source_cache_record(load_example("minimal_source_cache_record_v0.json"))
        record["truth_boundary"]["source_cache_record_can_mutate_master_index"] = True
        errors = source_cache.validate_source_cache_record(record)
        self.assertTrue(any("mutate_master_index" in error for error in errors), errors)

    def test_rights_malware_installability_and_exhaustive_claims_are_rejected(self) -> None:
        record = source_cache.build_source_cache_record(load_example("minimal_source_cache_record_v0.json"))
        record["rights_risk_posture"]["rights_clearance_claimed"] = True
        record["rights_risk_posture"]["malware_safety_claimed"] = True
        record["rights_risk_posture"]["verified_installability_claimed"] = True
        record["truth_boundary"]["source_cache_record_can_claim_exhaustive_global_search"] = True
        errors = source_cache.validate_source_cache_record(record)
        self.assertTrue(any("rights_clearance_claimed" in error for error in errors), errors)
        self.assertTrue(any("malware_safety_claimed" in error for error in errors), errors)
        self.assertTrue(any("verified_installability_claimed" in error for error in errors), errors)
        self.assertTrue(any("exhaustive_global_search" in error for error in errors), errors)

    def test_product_boundary_true_claim_fails(self) -> None:
        record = source_cache.build_source_cache_record(load_example("minimal_source_cache_record_v0.json"))
        record["product_boundary"]["enabled_network_access"] = True
        errors = source_cache.validate_source_cache_record(record)
        self.assertTrue(any("enabled_network_access" in error for error in errors), errors)

    def test_snapshot_is_review_gated_and_not_master_index(self) -> None:
        records = [source_cache.build_source_cache_record(load_example("minimal_source_cache_record_v0.json"))]
        snapshot = source_cache.build_source_cache_snapshot(records)
        self.assertEqual(snapshot["source_cache_record_count"], 1)
        self.assertFalse(snapshot["truth_boundary"]["source_cache_snapshot_is_master_index"])
        self.assertEqual(snapshot["review_required_count"], 1)

    def test_runtime_does_not_import_network_model_or_provider_modules(self) -> None:
        source = (REPO_ROOT / "runtime/local_foundry/source_cache.py").read_text(encoding="utf-8")
        forbidden = ["requests", "urllib", "http.client", "socket", "openai", "anthropic", "selenium", "playwright"]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_runtime_does_not_create_private_roots_or_master_index(self) -> None:
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)
        record = source_cache.build_source_cache_record(load_example("minimal_source_cache_record_v0.json"))
        self.assertFalse(record["product_boundary"]["mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
