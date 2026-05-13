import json
import re
import unittest
from pathlib import Path

from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.quality_delta import (
    build_h1_quality_delta,
    detect_h1_quality_overclaim,
)
from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.review_integration import (
    build_h1_candidate_promotion_preview,
    build_h1_evidence_candidate_review_seed,
    build_h1_review_integration_result,
    build_h1_source_cache_review_seed,
    build_h1_source_pack_update_preview,
    detect_h1_review_product_boundary_violations,
    detect_h1_review_truth_boundary_violations,
    load_h1_outputs,
)
from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.wave_postmortem import (
    build_h1_connector_wave_postmortem,
    build_h1_integration_audit,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
REPLAY_DIR = REPO_ROOT / "examples/connectors/h1_metadata_wave/replay_results"
LIVE_DIR = REPO_ROOT / "examples/connectors/h1_metadata_wave/live_probe_results"
RUNTIME_FILES = (
    REPO_ROOT / "control/prototypes/legacy_runtime/connectors/h1_metadata_wave/review_integration.py",
    REPO_ROOT / "control/prototypes/legacy_runtime/connectors/h1_metadata_wave/quality_delta.py",
    REPO_ROOT / "control/prototypes/legacy_runtime/connectors/h1_metadata_wave/wave_postmortem.py",
)


def load_outputs():
    return load_h1_outputs(sorted(REPLAY_DIR.glob("*.json")) + sorted(LIVE_DIR.glob("*.json")))


class H1ReviewIntegrationQualityTest(unittest.TestCase):
    def setUp(self):
        self.outputs = load_outputs()
        self.result = build_h1_review_integration_result({"outputs": self.outputs})
        self.delta = build_h1_quality_delta({"review_integration_result": self.result})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        self.assertEqual(self.result["schema_version"], "h1_review_integration_result.v0")
        self.assertEqual(len(self.result["sources"]), 7)
        self.assertEqual(len(self.result["source_cache_review_seeds"]), 7)
        self.assertEqual(len(self.result["evidence_candidate_review_seeds"]), 7)

    def test_review_integration_records_blocked_live_probe_outputs(self):
        self.assertEqual(sorted(self.result["blocked_sources"]), sorted(self.result["sources"]))

    def test_source_cache_review_seed_is_not_source_acceptance(self):
        seed = build_h1_source_cache_review_seed(self.outputs[0])
        self.assertFalse(seed["accepted_source_truth"])
        self.assertFalse(seed["source_cache_runtime_mutated"])
        self.assertFalse(seed["truth_boundary"]["source_cache_review_seed_accepts_source"])

    def test_evidence_candidate_review_seed_is_not_evidence_acceptance(self):
        seed = build_h1_evidence_candidate_review_seed(self.outputs[0])
        self.assertFalse(seed["accepted_evidence"])
        self.assertFalse(seed["evidence_ledger_runtime_mutated"])
        self.assertFalse(seed["truth_boundary"]["evidence_review_seed_accepts_evidence"])

    def test_candidate_promotion_preview_does_not_promote(self):
        preview = build_h1_candidate_promotion_preview(
            {
                "source_cache_review_seeds": self.result["source_cache_review_seeds"],
                "evidence_candidate_review_seeds": self.result["evidence_candidate_review_seeds"],
            }
        )
        self.assertFalse(preview["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(preview["accepted_candidate_truth"])

    def test_source_pack_update_preview_is_not_import_submission_or_acceptance(self):
        preview = build_h1_source_pack_update_preview({"sources": self.result["sources"]})
        self.assertFalse(preview["source_pack_imported"])
        self.assertFalse(preview["source_pack_submitted"])
        self.assertFalse(preview["source_pack_accepted"])
        self.assertFalse(preview["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_counts_fixture_live_and_blocked_sources(self):
        self.assertEqual(self.delta["source_count"], 7)
        self.assertEqual(self.delta["fixture_sources_count"], 7)
        self.assertEqual(self.delta["live_probe_sources_count"], 0)
        self.assertEqual(self.delta["blocked_sources_count"], 7)
        self.assertEqual(self.delta["review_seed_count"], 14)

    def test_quality_delta_rejects_production_and_external_superiority_claims(self):
        delta = dict(self.delta)
        delta["claims_production_readiness"] = True
        self.assertTrue(detect_h1_quality_overclaim(delta))
        delta = dict(self.delta)
        delta["claims_external_superiority"] = True
        self.assertTrue(detect_h1_quality_overclaim(delta))

    def test_postmortem_does_not_auto_approve_future_connectors(self):
        postmortem = build_h1_connector_wave_postmortem(self.result, self.delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        self.assertFalse(postmortem["truth_boundary"]["h1_postmortem_enables_future_connectors_automatically"])

    def test_h1_audit_returns_explicit_exit_gate_and_f_recommendation(self):
        postmortem = build_h1_connector_wave_postmortem(self.result, self.delta)
        audit = build_h1_integration_audit(self.result, self.delta, postmortem)
        self.assertEqual(audit["h1_exit_gate"], "PASS_WITH_WARNINGS")
        self.assertEqual(audit["next_phase_recommendation"], "READY_FOR_F_BUNDLE_01")

    def test_boundary_claims_are_rejected(self):
        for key in ("public_index_mutated", "master_index_mutated", "rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"):
            with self.subTest(key=key):
                seed = json.loads(json.dumps(self.result["source_cache_review_seeds"][0]))
                seed["truth_boundary"][key] = True
                self.assertTrue(detect_h1_review_truth_boundary_violations(seed))

    def test_product_boundary_claim_is_rejected(self):
        seed = json.loads(json.dumps(self.result["source_cache_review_seeds"][0]))
        seed["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h1_review_product_boundary_violations(seed))

    def test_runtime_does_not_call_network_or_model_provider(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in RUNTIME_FILES)
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))


if __name__ == "__main__":
    unittest.main()
