from __future__ import annotations

import copy
import unittest

from scripts import validate_h14_source_discovery_policy_packs as validator


class H14SourceDiscoveryPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_enablement_flags_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/source_need_registry_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "source_discovery_enabled", "live_access_enabled", "network_access_enabled",
            "model_provider_enabled", "source_sync_enabled", "connector_runtime_enabled",
            "source_registry_mutation_enabled", "connector_registry_mutation_enabled",
            "source_pack_export_enabled", "source_pack_import_enabled",
            "public_index_write_enabled", "master_index_write_enabled",
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = True
            self.assertTrue(validator.validate_source_record("source_need_registry", mutated, known), key)

    def test_policy_pack_granting_discovery_or_pack_permission_fails(self) -> None:
        pack = validator._load_json(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/policies/source_need_registry_policy_pack_v0.json")
        mutated = copy.deepcopy(pack)
        mutated["policy_pack_grants_discovery_access"] = True
        self.assertTrue(validator.validate_policy_pack("source_need_registry", mutated))
        mutated = copy.deepcopy(pack)
        mutated["source_pack_export_enabled"] = True
        self.assertTrue(validator.validate_policy_pack("source_need_registry", mutated))

    def test_preview_overclaims_fail(self) -> None:
        coverage = validator._load_json(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/coverage/h14_source_discovery_coverage_preview_v0.json")
        coverage["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage))
        scorecard = validator._load_json(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/scorecards/h14_source_discovery_scorecard_preview_v0.json")
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))
        scorecard["production_ready"] = False
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))

    def test_truth_and_forbidden_payload_claims_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/source_need_registry_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "source_candidate_is_source_truth", "source_discovery_candidate_is_registry_mutation",
            "connector_scorecard_is_connector_approval", "reliability_score_is_reliability_truth",
            "freshness_score_is_currentness_truth", "dispute_revocation_candidate_is_accepted_truth",
            "lineage_provenance_candidate_is_lineage_truth", "public_index_mutated",
            "master_index_mutated", "source_registry_mutated", "connector_registry_mutated",
            "source_completeness_claimed", "legal_approval_claimed", "rights_clearance_claimed",
            "production_readiness_claimed", "launch_readiness_claimed",
        ):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(validator.validate_source_record("source_need_registry", mutated, known), key)
        for payload_key in (
            "network_output", "api_output", "model_provider_output", "crawled_data",
            "scraped_data", "source_registry_write", "connector_registry_write",
            "source_cache_write", "public_index_write", "imported_pack", "exported_pack",
            "signed_pack", "private_data_payload", "artifact_payload",
        ):
            errors: list[str] = []
            validator._scan_forbidden_payload_keys("synthetic", {payload_key: "not allowed"}, errors)
            self.assertTrue(errors, payload_key)


if __name__ == "__main__":
    unittest.main()
