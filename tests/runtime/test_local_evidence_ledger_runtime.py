import json
import unittest
from pathlib import Path

from runtime.local_foundry import evidence_ledger


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_example(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples/evidence_ledger_records" / name).read_text(encoding="utf-8"))


class LocalEvidenceLedgerRuntimeTests(unittest.TestCase):
    def test_build_evidence_ledger_record_works_on_metadata_claim_example(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("metadata_claim_record_v0.json"))
        self.assertEqual(record["evidence_record_type"], "metadata_claim")
        self.assertEqual(record["evidence_record_status"], "metadata_claim_candidate")
        self.assertFalse(record["truth_boundary"]["evidence_record_is_public_truth"])
        self.assertFalse(record["truth_boundary"]["evidence_record_is_accepted_evidence"])

    def test_identity_claim_record_classifies_correctly(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("identity_claim_record_v0.json"))
        self.assertEqual(evidence_ledger.classify_evidence_record_type(record), "identity_claim")

    def test_compatibility_claim_record_classifies_correctly(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("compatibility_claim_record_v0.json"))
        self.assertEqual(evidence_ledger.classify_evidence_record_type(record), "compatibility_claim")

    def test_checksum_claim_record_classifies_correctly(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("checksum_claim_record_v0.json"))
        self.assertEqual(evidence_ledger.classify_evidence_record_type(record), "checksum_claim")

    def test_filename_member_claim_record_classifies_correctly(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("filename_member_claim_record_v0.json"))
        self.assertEqual(evidence_ledger.classify_evidence_record_type(record), "filename_or_member_claim")

    def test_source_locator_record_classifies_correctly(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("source_locator_record_v0.json"))
        self.assertEqual(evidence_ledger.classify_evidence_record_type(record), "source_locator")

    def test_pack_claim_record_remains_candidate_only(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("pack_claim_record_v0.json"))
        self.assertEqual(record["evidence_record_type"], "pack_claim")
        self.assertEqual(record["evidence_record_status"], "pack_claim_candidate")
        self.assertFalse(record["truth_boundary"]["evidence_record_is_accepted_evidence"])

    def test_conflicting_evidence_record_preserves_conflict_and_does_not_merge(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("conflicting_evidence_record_v0.json"))
        self.assertEqual(record["evidence_record_status"], "conflicting")
        self.assertEqual(record["evidence_record_type"], "conflict_record")
        self.assertFalse(record["conflict_summary"]["automatic_merge_allowed"])
        self.assertFalse(record["conflict_summary"]["automatic_conflict_resolution_allowed"])

    def test_policy_blocked_evidence_record_remains_policy_blocked(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("policy_blocked_evidence_record_v0.json"))
        self.assertEqual(record["evidence_record_status"], "policy_blocked")

    def test_evidence_truth_boundary_violation_is_rejected(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("minimal_evidence_record_v0.json"))
        record["truth_boundary"]["evidence_record_is_public_truth"] = True
        self.assertTrue(evidence_ledger.detect_evidence_truth_boundary_violations(record))
        self.assertTrue(evidence_ledger.validate_evidence_ledger_record(record))

    def test_accepted_evidence_claim_is_rejected(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("minimal_evidence_record_v0.json"))
        record["truth_boundary"]["evidence_record_is_accepted_evidence"] = True
        errors = evidence_ledger.validate_evidence_ledger_record(record)
        self.assertTrue(any("accepted_evidence" in error for error in errors), errors)

    def test_master_index_mutation_claim_is_rejected(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("minimal_evidence_record_v0.json"))
        record["truth_boundary"]["evidence_record_can_mutate_master_index"] = True
        errors = evidence_ledger.validate_evidence_ledger_record(record)
        self.assertTrue(any("mutate_master_index" in error for error in errors), errors)

    def test_rights_malware_installability_and_exhaustive_claims_are_rejected(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("minimal_evidence_record_v0.json"))
        record["rights_risk_posture"]["rights_clearance_claimed"] = True
        record["rights_risk_posture"]["malware_safety_claimed"] = True
        record["rights_risk_posture"]["verified_installability_claimed"] = True
        record["truth_boundary"]["evidence_record_can_claim_exhaustive_global_search"] = True
        errors = evidence_ledger.validate_evidence_ledger_record(record)
        self.assertTrue(any("rights_clearance_claimed" in error for error in errors), errors)
        self.assertTrue(any("malware_safety_claimed" in error for error in errors), errors)
        self.assertTrue(any("verified_installability_claimed" in error for error in errors), errors)
        self.assertTrue(any("exhaustive_global_search" in error for error in errors), errors)

    def test_ai_draft_marked_evidence_truth_is_rejected(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(
            {"evidence_label": "AI Draft", "evidence_record_type": "ai_draft_future", "truth_boundary": {"evidence_record_is_accepted_evidence": True}}
        )
        errors = evidence_ledger.validate_evidence_ledger_record(record)
        self.assertTrue(errors)

    def test_discussion_derived_truth_claim_is_rejected(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(
            {"evidence_label": "Discussion", "evidence_record_type": "discussion_derived_future", "notes": ["discussion derived truth"]}
        )
        errors = evidence_ledger.validate_evidence_ledger_record(record)
        self.assertTrue(errors)

    def test_product_boundary_true_claim_fails(self) -> None:
        record = evidence_ledger.build_evidence_ledger_record(load_example("minimal_evidence_record_v0.json"))
        record["product_boundary"]["enabled_network_access"] = True
        errors = evidence_ledger.validate_evidence_ledger_record(record)
        self.assertTrue(any("enabled_network_access" in error for error in errors), errors)

    def test_snapshot_preserves_conflict_summary(self) -> None:
        records = [
            evidence_ledger.build_evidence_ledger_record(load_example("metadata_claim_record_v0.json")),
            evidence_ledger.build_evidence_ledger_record(load_example("conflicting_evidence_record_v0.json")),
        ]
        snapshot = evidence_ledger.build_evidence_ledger_snapshot(records)
        self.assertEqual(snapshot["conflict_summary"]["conflicting_record_count"], 1)
        self.assertFalse(snapshot["conflict_summary"]["automatic_merge_allowed"])

    def test_runtime_does_not_import_network_model_or_provider_modules(self) -> None:
        source = (REPO_ROOT / "runtime/local_foundry/evidence_ledger.py").read_text(encoding="utf-8")
        forbidden = ["requests", "urllib", "http.client", "socket", "openai", "anthropic", "selenium", "playwright"]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_runtime_does_not_create_private_roots_or_master_index(self) -> None:
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)
        record = evidence_ledger.build_evidence_ledger_record(load_example("minimal_evidence_record_v0.json"))
        self.assertFalse(record["product_boundary"]["mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
