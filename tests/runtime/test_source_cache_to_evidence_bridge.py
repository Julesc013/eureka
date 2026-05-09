import json
import unittest
from pathlib import Path

from runtime.local_foundry import evidence_ledger, source_cache, source_cache_to_evidence


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_source_cache_example(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples/source_cache_records" / name).read_text(encoding="utf-8"))


class SourceCacheToEvidenceBridgeRuntimeTests(unittest.TestCase):
    def bridge(self, name: str) -> tuple[dict, list[dict], dict]:
        source_record = source_cache.build_source_cache_record(load_source_cache_example(name))
        candidates = source_cache_to_evidence.map_source_cache_record_to_evidence_candidates(source_record)
        result = source_cache_to_evidence.build_bridge_result(source_record, candidates)
        return source_record, candidates, result

    def test_source_metadata_record_maps_to_metadata_claim_candidate(self) -> None:
        _source_record, candidates, result = self.bridge("source_metadata_record_v0.json")
        self.assertEqual(result["bridge_status"], "evidence_candidate_created")
        self.assertEqual(candidates[0]["evidence_record_type"], "metadata_claim")
        self.assertEqual(candidates[0]["evidence_record_status"], "metadata_claim_candidate")

    def test_source_locator_record_maps_to_source_observation_candidate(self) -> None:
        _source_record, candidates, result = self.bridge("source_locator_record_v0.json")
        self.assertEqual(result["bridge_status"], "evidence_candidate_created")
        self.assertEqual(candidates[0]["evidence_record_type"], "source_observation")
        self.assertEqual(candidates[0]["evidence_record_status"], "source_observation_candidate")

    def test_source_policy_record_maps_to_source_observation_candidate(self) -> None:
        _source_record, candidates, result = self.bridge("source_policy_record_v0.json")
        self.assertEqual(candidates[0]["evidence_record_type"], "source_observation")
        self.assertEqual(candidates[0]["claim_type"], "source_observation")
        self.assertFalse(result["truth_boundary"]["bridge_output_is_accepted_evidence"])

    def test_source_coverage_record_maps_to_metadata_claim_candidate(self) -> None:
        _source_record, candidates, _result = self.bridge("source_coverage_record_v0.json")
        self.assertEqual(candidates[0]["evidence_record_type"], "metadata_claim")
        self.assertEqual(candidates[0]["claim_type"], "metadata")

    def test_policy_blocked_source_cache_record_remains_policy_blocked(self) -> None:
        _source_record, candidates, result = self.bridge("policy_blocked_source_cache_record_v0.json")
        self.assertEqual(result["bridge_status"], "policy_blocked")
        self.assertEqual(candidates[0]["evidence_record_status"], "policy_blocked")
        self.assertEqual(candidates[0]["evidence_record_type"], "review_status_record")

    def test_bridge_result_requires_review(self) -> None:
        _source_record, _candidates, result = self.bridge("source_metadata_record_v0.json")
        self.assertTrue(result["review_gates"]["human_review_required"])
        for mapping in result["mapping_results"]:
            self.assertTrue(mapping["review_required"])

    def test_generated_evidence_candidate_remains_unaccepted(self) -> None:
        _source_record, candidates, _result = self.bridge("source_metadata_record_v0.json")
        truth = candidates[0]["truth_boundary"]
        self.assertFalse(truth["evidence_record_is_public_truth"])
        self.assertFalse(truth["evidence_record_is_accepted_evidence"])
        self.assertFalse(truth["evidence_record_can_mutate_master_index"])

    def test_source_cache_record_cannot_become_accepted_evidence(self) -> None:
        record = source_cache.build_source_cache_record(load_source_cache_example("source_metadata_record_v0.json"))
        record["truth_boundary"]["source_cache_record_is_accepted_evidence"] = True
        errors = source_cache_to_evidence.detect_forbidden_source_cache_conversion(record)
        self.assertTrue(any("accepted_evidence" in error for error in errors), errors)

    def test_source_observation_cannot_become_accepted_truth(self) -> None:
        _source_record, candidates, result = self.bridge("source_locator_record_v0.json")
        result["truth_boundary"]["bridge_output_is_accepted_public_truth"] = True
        errors = source_cache_to_evidence.validate_bridge_result(result)
        self.assertTrue(any("accepted_public_truth" in error for error in errors), errors)
        self.assertEqual(candidates[0]["evidence_record_type"], "source_observation")

    def test_metadata_claim_cannot_become_rights_clearance(self) -> None:
        _source_record, candidates, _result = self.bridge("source_metadata_record_v0.json")
        candidate = dict(candidates[0])
        candidate["truth_boundary"] = dict(candidate["truth_boundary"])
        candidate["truth_boundary"]["evidence_record_can_claim_rights_clearance"] = True
        errors = source_cache_to_evidence.validate_bridge_evidence_candidate(candidate)
        self.assertTrue(any("rights_clearance" in error for error in errors), errors)

    def test_checksum_and_compatibility_forbidden_conversions_are_declared(self) -> None:
        policy = source_cache_to_evidence.default_policy()
        self.assertIn("checksum_claim_to_authenticity_proof_without_review", policy["forbidden_conversions"])
        self.assertIn("compatibility_claim_to_verified_compatibility_without_review", policy["forbidden_conversions"])

    def test_ai_draft_marked_evidence_truth_is_rejected(self) -> None:
        candidate = evidence_ledger.build_evidence_ledger_record(
            {
                "evidence_label": "AI Draft Candidate",
                "evidence_record_type": "ai_draft_future",
                "truth_boundary": {"evidence_record_is_accepted_evidence": True},
            }
        )
        self.assertTrue(source_cache_to_evidence.validate_bridge_evidence_candidate(candidate))

    def test_master_index_mutation_claim_is_rejected(self) -> None:
        _source_record, _candidates, result = self.bridge("source_metadata_record_v0.json")
        result["truth_boundary"]["bridge_output_can_mutate_master_index"] = True
        errors = source_cache_to_evidence.validate_bridge_result(result)
        self.assertTrue(any("mutate_master_index" in error for error in errors), errors)

    def test_product_boundary_true_claim_fails(self) -> None:
        _source_record, _candidates, result = self.bridge("source_metadata_record_v0.json")
        result["product_boundary"]["enabled_network_access"] = True
        errors = source_cache_to_evidence.validate_bridge_result(result)
        self.assertTrue(any("enabled_network_access" in error for error in errors), errors)

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        source = (REPO_ROOT / "runtime/local_foundry/source_cache_to_evidence.py").read_text(encoding="utf-8")
        forbidden = ["requests", "urllib", "http.client", "socket", "openai", "anthropic", "selenium", "playwright"]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        _source_record, _candidates, result = self.bridge("source_metadata_record_v0.json")
        self.assertFalse(result["product_boundary"]["mutated_master_index"])
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
