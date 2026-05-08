from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from runtime.local_foundry import candidate_store


ROOT = Path(__file__).resolve().parents[2]


class CandidateStoreRuntimeTests(unittest.TestCase):
    def test_build_candidate_record_works_on_search_need_example(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/search_needs/software_version_search_need_v0.json"))

        self.assertEqual(record["candidate_origin"], "search_need")
        self.assertEqual(record["candidate_type"], "version_or_state_candidate")
        self.assertEqual(candidate_store.validate_candidate_record(record), [])

    def test_source_lead_candidate_classifies_correctly(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/candidates/source_lead_candidate_v0.json"))

        self.assertEqual(record["candidate_type"], "source_lead_candidate")
        self.assertEqual(record["candidate_origin"], "source_lead")

    def test_workunit_result_candidate_classifies_correctly(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/work_unit_results/search_need_review_pass_v0/work_unit_result.json"))

        self.assertEqual(record["candidate_type"], "workunit_seed_candidate")
        self.assertEqual(record["candidate_origin"], "workunit_result")

    def test_policy_blocked_candidate_remains_policy_blocked(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/candidates/policy_blocked_candidate_v0.json"))

        self.assertEqual(record["candidate_status"], "policy_blocked")
        self.assertEqual(record["candidate_type"], "policy_blocked_candidate")

    def test_duplicate_possible_candidate_is_not_merged(self) -> None:
        records = [
            _json("examples/candidates/search_need_candidate_v0.json"),
            _json("examples/candidates/duplicate_possible_candidate_v0.json"),
        ]

        report = candidate_store.deduplicate_candidate_records(records)

        self.assertEqual(report["duplicate_group_count"], 1)
        self.assertFalse(report["automatic_merge_allowed"])
        self.assertEqual(report["merged_candidate_ids"], [])
        self.assertEqual(report["deleted_candidate_ids"], [])

    def test_candidate_truth_boundary_violation_is_rejected(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/candidates/minimal_candidate_v0.json"))
        record["truth_boundary"]["candidate_is_public_truth"] = True

        errors = candidate_store.detect_candidate_truth_boundary_violations(record)

        self.assertTrue(any("candidate_is_public_truth" in error for error in errors))

    def test_accepted_evidence_claim_is_rejected(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/candidates/minimal_candidate_v0.json"))
        record["truth_boundary"]["candidate_is_accepted_evidence"] = True

        errors = candidate_store.validate_candidate_record(record)

        self.assertTrue(any("candidate_is_accepted_evidence" in error for error in errors))

    def test_master_index_mutation_claim_is_rejected(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/candidates/minimal_candidate_v0.json"))
        record["truth_boundary"]["candidate_can_mutate_master_index"] = True

        errors = candidate_store.validate_candidate_record(record)

        self.assertTrue(any("candidate_can_mutate_master_index" in error for error in errors))

    def test_rights_malware_installability_exhaustive_claims_are_rejected(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/candidates/minimal_candidate_v0.json"))
        record["truth_boundary"]["candidate_can_claim_rights_clearance"] = True
        record["truth_boundary"]["candidate_can_claim_malware_safety"] = True
        record["truth_boundary"]["candidate_can_claim_verified_installability"] = True
        record["truth_boundary"]["candidate_can_claim_exhaustive_global_search"] = True

        errors = candidate_store.validate_candidate_record(record)

        self.assertTrue(any("candidate_can_claim_rights_clearance" in error for error in errors))
        self.assertTrue(any("candidate_can_claim_malware_safety" in error for error in errors))
        self.assertTrue(any("candidate_can_claim_verified_installability" in error for error in errors))
        self.assertTrue(any("candidate_can_claim_exhaustive_global_search" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        record = candidate_store.build_candidate_record(_json("examples/candidates/minimal_candidate_v0.json"))
        record["product_boundary"]["enabled_telemetry"] = True

        errors = candidate_store.detect_candidate_product_boundary_violations(record)

        self.assertTrue(any("enabled_telemetry" in error for error in errors))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            record = candidate_store.build_candidate_record(_json("examples/search_needs/driver_search_need_v0.json"))
            summary = candidate_store.summarize_candidate_record(record)

        self.assertFalse(summary["candidate_is_public_truth"])
        self.assertFalse(record["product_boundary"]["enabled_model_provider_calls"])

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        before = _private_root_state()

        snapshot = candidate_store.build_candidate_store_snapshot([_json("examples/candidates/minimal_candidate_v0.json")])

        self.assertFalse(snapshot["truth_boundary"]["candidate_store_is_master_index"])
        self.assertFalse(snapshot["product_boundary"]["mutated_master_index"])
        self.assertEqual(before, _private_root_state())


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (ROOT / ".aide.local").exists(),
        ".local/eureka": (ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (ROOT / ".cache" / "eureka").exists(),
    }


if __name__ == "__main__":
    unittest.main()

