import json
import re
import unittest
from pathlib import Path

from archive.prototypes.legacy_runtime.connectors.h2_package_registries.quality_delta import build_h2_quality_delta, detect_h2_quality_overclaim
from archive.prototypes.legacy_runtime.connectors.h2_package_registries.review_integration import (
    build_h2_candidate_promotion_preview,
    build_h2_dependency_candidate_review_seed,
    build_h2_evidence_candidate_review_seed,
    build_h2_package_file_candidate_review_seed,
    build_h2_package_identity_review_seed,
    build_h2_review_integration_result,
    build_h2_source_cache_review_seed,
    build_h2_source_pack_update_preview,
    detect_h2_review_product_boundary_violations,
    detect_h2_review_truth_boundary_violations,
    load_h2_package_outputs,
)
from archive.prototypes.legacy_runtime.connectors.h2_package_registries.wave_postmortem import build_h2_connector_wave_postmortem, build_h2_integration_audit


REPO_ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = REPO_ROOT / "examples/connectors/h2_package_registries/replay_results"
LIVE_DIR = REPO_ROOT / "examples/connectors/h2_package_registries/live_probe_results"
RUNTIME_FILES = (
    REPO_ROOT / "archive/prototypes/legacy_runtime/connectors/h2_package_registries/review_integration.py",
    REPO_ROOT / "archive/prototypes/legacy_runtime/connectors/h2_package_registries/quality_delta.py",
    REPO_ROOT / "archive/prototypes/legacy_runtime/connectors/h2_package_registries/wave_postmortem.py",
)


def load_outputs():
    return load_h2_package_outputs(sorted(REPLAY_DIR.glob("*.json")) + sorted(LIVE_DIR.glob("*.json")))


class H2PackageReviewIntegrationQualityTest(unittest.TestCase):
    def setUp(self):
        self.outputs = load_outputs()
        self.result = build_h2_review_integration_result({"outputs": self.outputs})
        self.delta = build_h2_quality_delta({"review_integration_result": self.result})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        self.assertEqual(self.result["schema_version"], "h2_package_review_integration_result.v0")
        self.assertEqual(len(self.result["sources"]), 8)
        self.assertEqual(len(self.result["package_identity_review_seeds"]), 8)
        self.assertEqual(len(self.result["source_cache_review_seeds"]), 8)
        self.assertEqual(len(self.result["evidence_candidate_review_seeds"]), 8)

    def test_review_integration_records_blocked_live_probe_outputs(self):
        self.assertEqual(sorted(self.result["blocked_sources"]), sorted(self.result["sources"]))

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        record = self.outputs[0]["connector_output_envelope"]["normalized_record"]
        live = {
            "schema_version": "h2_package_live_probe_result.v0",
            "source_id": record["source_id"],
            "result_status": "live_probe_completed",
            "request_count": 1,
            "network_used": False,
            "normalized_record": record,
            "truth_boundary": {"public_index_mutated": False},
            "product_boundary": {"mutated_public_index": False},
        }
        result = build_h2_review_integration_result({"outputs": [live]})
        self.assertEqual(result["sources"], [record["source_id"]])
        self.assertEqual(len(result["package_identity_review_seeds"]), 1)

    def test_package_identity_review_seed_is_not_identity_truth(self):
        seed = build_h2_package_identity_review_seed(self.outputs[0])
        self.assertFalse(seed["accepted_package_identity_truth"])
        self.assertFalse(seed["truth_boundary"]["package_identity_seed_accepts_identity"])

    def test_dependency_candidate_review_seed_is_not_dependency_correctness(self):
        seed = build_h2_dependency_candidate_review_seed(self.outputs[0])
        self.assertFalse(seed["accepted_dependency_correctness"])
        self.assertFalse(seed["truth_boundary"]["dependency_seed_accepts_correctness"])

    def test_package_file_review_seed_is_not_download_or_malware_safety(self):
        seed = build_h2_package_file_candidate_review_seed(self.outputs[0])
        self.assertFalse(seed["download_allowed_current"])
        self.assertFalse(seed["package_file_seed_grants_download_or_safety"])

    def test_source_cache_review_seed_is_not_source_acceptance(self):
        seed = build_h2_source_cache_review_seed(self.outputs[0])
        self.assertFalse(seed["accepted_source_truth"])
        self.assertFalse(seed["source_cache_runtime_mutated"])

    def test_evidence_candidate_review_seed_is_not_evidence_acceptance(self):
        seed = build_h2_evidence_candidate_review_seed(self.outputs[0])
        self.assertFalse(seed["accepted_evidence"])
        self.assertFalse(seed["evidence_ledger_runtime_mutated"])

    def test_candidate_promotion_preview_does_not_promote(self):
        preview = build_h2_candidate_promotion_preview(self.result)
        self.assertFalse(preview["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(preview["accepted_candidate_truth"])

    def test_source_pack_update_preview_is_not_import_submission_or_acceptance(self):
        preview = build_h2_source_pack_update_preview({"sources": self.result["sources"]})
        self.assertFalse(preview["source_pack_imported"])
        self.assertFalse(preview["source_pack_submitted"])
        self.assertFalse(preview["source_pack_accepted"])

    def test_quality_delta_counts_fixture_live_and_blocked_sources(self):
        self.assertEqual(self.delta["source_count"], 8)
        self.assertEqual(self.delta["fixture_sources_count"], 8)
        self.assertEqual(self.delta["live_probe_sources_count"], 0)
        self.assertEqual(self.delta["blocked_sources_count"], 8)
        self.assertGreaterEqual(self.delta["review_seed_count"], 40)

    def test_quality_delta_rejects_forbidden_claims(self):
        for key in ("package_installability_verified", "dependency_correctness_verified", "rights_clearance", "malware_safety", "production_search_quality"):
            delta = dict(self.delta)
            delta[key] = True
            self.assertTrue(detect_h2_quality_overclaim(delta))

    def test_postmortem_does_not_auto_approve_future_connectors(self):
        postmortem = build_h2_connector_wave_postmortem(self.result, self.delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])

    def test_h2_audit_returns_explicit_exit_gate_and_h3_recommendation(self):
        postmortem = build_h2_connector_wave_postmortem(self.result, self.delta)
        audit = build_h2_integration_audit(self.result, self.delta, postmortem)
        self.assertEqual(audit["h2_exit_gate"], "PASS_WITH_WARNINGS")
        self.assertEqual(audit["next_phase_recommendation"], "READY_FOR_H3_BUNDLE_01")

    def test_boundary_claims_are_rejected(self):
        for key in ("public_index_mutated", "master_index_mutated", "rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"):
            seed = json.loads(json.dumps(self.result["package_identity_review_seeds"][0]))
            seed["truth_boundary"][key] = True
            self.assertTrue(detect_h2_review_truth_boundary_violations(seed))

    def test_product_boundary_claim_is_rejected(self):
        seed = json.loads(json.dumps(self.result["package_file_candidate_review_seeds"][0]))
        seed["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h2_review_product_boundary_violations(seed))

    def test_runtime_does_not_call_network_or_model_provider(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in RUNTIME_FILES)
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))


if __name__ == "__main__":
    unittest.main()
