from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts import validate_reviewed_public_index_rebuild_contract as validator


REPO_ROOT = Path(__file__).resolve().parents[2]


class ReviewedPublicIndexRebuildContractTest(unittest.TestCase):
    def test_contract_json_is_valid_and_declares_boundaries(self) -> None:
        for raw_path in validator.CONTRACT_PATHS:
            with self.subTest(path=raw_path):
                payload = _read_json(raw_path)
                errors = validator.validate_contract_payload(payload, raw_path)
                self.assertEqual(errors, [])
                self.assertTrue(payload["x-contract_only"])
                self.assertTrue(payload["x-no_public_index_mutation"])
                self.assertTrue(payload["x-no_master_index_mutation"])
                self.assertTrue(payload["x-no_auto_acceptance"])

    def test_valid_rebuild_examples_pass(self) -> None:
        for raw_path in validator.EXAMPLE_REBUILD_PATHS:
            with self.subTest(path=raw_path):
                payload = _read_json(raw_path)
                self.assertEqual(validator.validate_rebuild_payload(payload, raw_path, REPO_ROOT), [])

    def test_valid_public_record_proposal_examples_pass(self) -> None:
        for raw_path in validator.EXAMPLE_PROPOSAL_PATHS:
            with self.subTest(path=raw_path):
                payload = _read_json(raw_path)
                self.assertEqual(validator.validate_proposal_payload(payload, raw_path, REPO_ROOT), [])

    def test_invalid_rebuild_status_fails(self) -> None:
        payload = _rebuild()
        payload["rebuild_status"] = "rebuilt_now"
        errors = validator.validate_rebuild_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("rebuild_status" in error for error in errors))

    def test_invalid_proposal_status_fails(self) -> None:
        payload = _proposal()
        payload["proposal_status"] = "published_now"
        errors = validator.validate_proposal_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("proposal_status" in error for error in errors))

    def test_invalid_proposal_type_fails(self) -> None:
        payload = _proposal()
        payload["proposal_type"] = "canonical_truth_record"
        errors = validator.validate_proposal_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("proposal_type" in error for error in errors))

    def test_forbidden_input_type_fails(self) -> None:
        payload = _rebuild()
        payload["reviewed_input_refs"].append(
            {
                "input_ref": "bad",
                "input_type": "scraped_result",
                "review_status": "none",
                "provenance_refs": [],
                "evidence_refs": [],
                "limitations": ["blocked"],
            }
        )
        errors = validator.validate_rebuild_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("forbidden input type" in error for error in errors))

    def test_forbidden_output_type_fails(self) -> None:
        payload = _rebuild()
        payload["rebuild_output_policy"]["allowed_output_types"].append("master_index_mutation")
        errors = validator.validate_rebuild_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("forbidden output type" in error for error in errors))

    def test_current_public_index_mutation_claim_fails(self) -> None:
        payload = _rebuild()
        payload["public_index_mutation_policy"]["public_index_mutation_allowed_current"] = True
        errors = validator.validate_rebuild_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("public_index_mutation_allowed_current" in error for error in errors))

    def test_current_master_index_mutation_claim_fails(self) -> None:
        payload = _rebuild()
        payload["master_index_mutation_policy"]["master_index_mutation_allowed_current"] = True
        errors = validator.validate_rebuild_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("master_index_mutation_allowed_current" in error for error in errors))

    def test_automatic_candidate_acceptance_fails(self) -> None:
        payload = _read_json("control/inventory/review/reviewed_public_index_truth_policy.json")
        payload["automatic_candidate_acceptance_allowed"] = True
        errors = validator.validate_truth_policy_payload(payload)
        self.assertTrue(any("automatic_candidate_acceptance_allowed" in error for error in errors))

    def test_automatic_evidence_acceptance_fails(self) -> None:
        payload = _read_json("control/inventory/review/reviewed_public_index_truth_policy.json")
        payload["automatic_evidence_acceptance_allowed"] = True
        errors = validator.validate_truth_policy_payload(payload)
        self.assertTrue(any("automatic_evidence_acceptance_allowed" in error for error in errors))

    def test_missing_evidence_ready_claim_fails(self) -> None:
        payload = _read_json("examples/reviewed_public_index_rebuilds/ready_candidate_rebuild_input_v0.json")
        payload["evidence_requirements"]["evidence_refs_present"] = False
        errors = validator.validate_rebuild_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("evidence refs present" in error for error in errors))

    def test_unresolved_conflict_without_preservation_fails(self) -> None:
        payload = _proposal()
        payload["conflict_summary"]["conflict_status"] = "conflict_detected"
        payload["conflict_summary"]["conflict_preserved"] = False
        errors = validator.validate_proposal_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("conflict" in error for error in errors))

    def test_duplicate_uncertainty_without_preservation_fails(self) -> None:
        payload = _proposal()
        payload["duplicate_summary"]["duplicate_status"] = "duplicate_possible"
        payload["duplicate_summary"]["duplicate_preserved"] = False
        errors = validator.validate_proposal_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("duplicate" in error for error in errors))

    def test_rights_malware_installability_exhaustive_search_claim_fails(self) -> None:
        payload = _proposal()
        payload["rights_summary"]["rights_clearance_claimed"] = True
        payload["risk_summary"]["malware_safety_claimed"] = True
        payload["risk_summary"]["verified_installability_claimed"] = True
        payload["product_boundary"]["claimed_exhaustive_global_search"] = True
        errors = validator.validate_proposal_payload(payload, "broken", REPO_ROOT)
        self.assertGreaterEqual(len(errors), 4)

    def test_path_policy_allowing_site_dist_fails(self) -> None:
        payload = _read_json("control/inventory/review/reviewed_public_index_path_policy.json")
        payload["allowed_output_roots_current"].append("site/dist/")
        errors = validator.validate_path_policy_payload(payload)
        self.assertTrue(any("site/dist" in error for error in errors))

    def test_path_policy_allowing_data_public_index_fails(self) -> None:
        payload = _read_json("control/inventory/review/reviewed_public_index_path_policy.json")
        payload["allowed_output_roots_current"].append("data/public_index/")
        errors = validator.validate_path_policy_payload(payload)
        self.assertTrue(any("data/public_index" in error for error in errors))

    def test_credential_fixture_fails(self) -> None:
        payload = _rebuild()
        payload["reviewed_input_refs"].append(
            {
                "input_ref": "credential.fixture",
                "input_type": "secret_or_credential",
                "review_status": "blocked",
                "provenance_refs": [],
                "evidence_refs": [],
                "limitations": ["blocked"],
            }
        )
        errors = validator.validate_rebuild_payload(payload, "broken", REPO_ROOT)
        self.assertTrue(any("forbidden input type" in error for error in errors))

    def test_validator_does_not_create_public_index_artifacts(self) -> None:
        before_site = (REPO_ROOT / "site/dist").exists()
        before_public_index = (REPO_ROOT / "data/public_index").exists()
        report = validator.validate_reviewed_public_index_rebuild_contract(REPO_ROOT)
        self.assertEqual(report["status"], "pass")
        self.assertEqual((REPO_ROOT / "site/dist").exists(), before_site)
        self.assertEqual((REPO_ROOT / "data/public_index").exists(), before_public_index)

    def test_validator_does_not_call_network_model_provider(self) -> None:
        source = (REPO_ROOT / "scripts/validate_reviewed_public_index_rebuild_contract.py").read_text(encoding="utf-8")
        forbidden = ["urllib", "requests", "http.client", "socket", "openai", "anthropic"]
        self.assertFalse(any(token in source for token in forbidden))


def _rebuild() -> dict:
    return deepcopy(_read_json("examples/reviewed_public_index_rebuilds/minimal_rebuild_contract_v0.json"))


def _proposal() -> dict:
    return deepcopy(_read_json("examples/reviewed_public_records/software_candidate_record_proposal_v0.json"))


def _read_json(raw_path: str) -> dict:
    return json.loads((REPO_ROOT / raw_path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
