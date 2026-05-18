import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class IAMetadataNonClaimTests(unittest.TestCase):
    def test_non_claim_policy_blocks_truth_inference(self):
        policy = load_json("control/policies/ia_non_claim_policy.json")
        for key in (
            "metadata_is_not_truth",
            "source_observation_material_only",
            "review_required_before_truth",
            "no_rights_claims_from_metadata_alone",
            "no_safety_claims_from_metadata_alone",
            "no_compatibility_truth_from_metadata_alone",
            "no_availability_truth_from_metadata_alone",
            "no_source_trust_inference_without_review",
            "live_ia_json_to_public_truth_forbidden",
        ):
            self.assertTrue(policy[key], key)

    def test_evidence_requirements_keep_candidates_unaccepted(self):
        requirements = load_json("control/inventory/ia_metadata_evidence_requirements.json")
        rows = {item["requirement_id"]: item for item in requirements["requirements"]}
        self.assertIn("no_accepted_truth_without_review", rows)
        self.assertIn("No IA metadata field becomes accepted Eureka truth", rows["no_accepted_truth_without_review"]["summary"])
        for requirement_id in (
            "title_claim_candidate",
            "mediatype_claim_candidate",
            "creator_date_description_claim_candidate_if_present",
            "file_list_claim_candidate",
            "checksum_file_metadata_claim_candidate",
            "source_locator_claim_candidate",
        ):
            self.assertIn(requirement_id, rows)
            self.assertIn("candidate", rows[requirement_id]["requirement_id"])

    def test_docs_state_metadata_is_not_truth(self):
        docs = [
            "docs/architecture/IA_METADATA_CONNECTOR_MODEL.md",
            "docs/operations/IA_METADATA_NON_CLAIMS.md",
            "docs/reference/IA_METADATA_FIELD_MAPPING.md",
        ]
        text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in docs).lower()
        self.assertIn("metadata is not truth", text)
        self.assertIn("not accepted identity without review", text)
        self.assertIn("no ia metadata field becomes accepted truth", text)

    def test_no_production_or_public_claims(self):
        for relative in (
            "control/policies/ia_metadata_connector_policy.json",
            "control/policies/ia_source_access_policy.json",
            "control/policies/ia_non_claim_policy.json",
            "control/inventory/ia_00_result.json",
        ):
            payload = load_json(relative)
            self.assertFalse(payload["production_readiness_claimed"], relative)
            self.assertFalse(payload["public_launch_readiness_claimed"], relative)


if __name__ == "__main__":
    unittest.main()
