import json
import re
import unittest
from pathlib import Path

from runtime.connectors.internet_archive.quality_delta import (
    build_h0_readiness_recommendation,
    build_ia_connector_postmortem,
    build_ia_quality_delta,
    detect_quality_overclaim,
)
from runtime.connectors.internet_archive.review_integration import (
    build_ia_candidate_promotion_dry_run,
    build_ia_evidence_candidate_review_entry,
    build_ia_pack_draft_preview,
    build_ia_source_cache_review_entry,
    detect_ia_review_product_boundary_violations,
    detect_ia_review_truth_boundary_violations,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
IA02_GENERATED = REPO_ROOT / "control/audits/ia-bundle-02-bounded-metadata-live-probe-v0/generated"
RUNTIME_FILES = (
    REPO_ROOT / "runtime/connectors/internet_archive/review_integration.py",
    REPO_ROOT / "runtime/connectors/internet_archive/quality_delta.py",
)


def load_json(name):
    return json.loads((IA02_GENERATED / name).read_text(encoding="utf-8"))


class InternetArchiveReviewIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.source_candidate = load_json("sample_source_cache_candidate_from_live_probe.json")
        self.evidence_preview = load_json("sample_evidence_candidate_preview_from_live_probe.json")
        self.source_entry = build_ia_source_cache_review_entry(self.source_candidate, None)
        self.evidence_entry = build_ia_evidence_candidate_review_entry(self.evidence_preview, None)

    def test_ia_source_cache_candidate_becomes_review_entry_only(self):
        self.assertEqual(self.source_entry["schema_version"], "internet_archive_source_cache_review_entry.v0")
        self.assertEqual(self.source_entry["review_integration_status"], "blocked_dry_run")
        self.assertFalse(self.source_entry["accepted_source_truth"])
        self.assertFalse(self.source_entry["source_cache_runtime_mutated"])

    def test_ia_evidence_candidate_becomes_review_entry_only(self):
        self.assertEqual(self.evidence_entry["schema_version"], "internet_archive_evidence_candidate_review_entry.v0")
        self.assertEqual(self.evidence_entry["review_integration_status"], "blocked_dry_run")
        self.assertFalse(self.evidence_entry["accepted_evidence"])
        self.assertFalse(self.evidence_entry["evidence_ledger_runtime_mutated"])

    def test_review_entry_does_not_accept_truth(self):
        for entry in (self.source_entry, self.evidence_entry):
            truth = entry["truth_boundary"]
            self.assertFalse(truth["ia_review_output_is_public_truth"])
            self.assertFalse(truth["ia_source_cache_review_entry_accepts_source"])
            self.assertFalse(truth["ia_evidence_review_entry_accepts_evidence"])
            self.assertFalse(truth["ia_candidate_promotion_dry_run_accepts_candidate"])

    def test_promotion_dry_run_does_not_promote_candidate(self):
        dry_run = build_ia_candidate_promotion_dry_run(
            {
                "source_cache_review_entry": self.source_entry,
                "evidence_review_entry": self.evidence_entry,
            },
            None,
        )
        self.assertEqual(dry_run["promotion_dry_run_status"], "policy_blocked")
        self.assertFalse(dry_run["candidate_promotion_dry_run_accepts_candidate"])
        self.assertFalse(dry_run["accepted_candidate_truth"])

    def test_pack_draft_preview_does_not_import_submit_or_accept_pack(self):
        dry_run = build_ia_candidate_promotion_dry_run(
            {
                "source_cache_review_entry": self.source_entry,
                "evidence_review_entry": self.evidence_entry,
            },
            None,
        )
        pack = build_ia_pack_draft_preview(
            {
                "source_cache_review_entry": self.source_entry,
                "evidence_review_entry": self.evidence_entry,
                "candidate_promotion_dry_run": dry_run,
            },
            None,
        )
        self.assertFalse(pack["pack_imported"])
        self.assertFalse(pack["pack_submitted"])
        self.assertFalse(pack["pack_accepted"])
        self.assertFalse(pack["truth_boundary"]["ia_pack_draft_is_accepted_pack"])

    def test_quality_delta_does_not_claim_production_readiness(self):
        delta = build_ia_quality_delta(
            {
                "source_cache_review_entry": self.source_entry,
                "evidence_review_entry": self.evidence_entry,
            },
            None,
        )
        self.assertFalse(delta["claims_production_readiness"])
        self.assertFalse(delta["truth_boundary"]["ia_quality_delta_is_production_claim"])

    def test_quality_delta_does_not_claim_external_superiority(self):
        delta = build_ia_quality_delta({"source_cache_review_entry": self.source_entry}, None)
        self.assertFalse(delta["claims_external_superiority"])
        delta["claims_external_superiority"] = True
        self.assertTrue(detect_quality_overclaim(delta, None))

    def test_connector_postmortem_does_not_auto_approve_future_connectors(self):
        outputs = {
            "source_cache_review_entry": self.source_entry,
            "evidence_review_entry": self.evidence_entry,
        }
        delta = build_ia_quality_delta(outputs, None)
        postmortem = build_ia_connector_postmortem(delta, outputs, None)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        self.assertFalse(postmortem["truth_boundary"]["ia_postmortem_enables_future_connectors_automatically"])
        h0 = build_h0_readiness_recommendation(postmortem, None)
        self.assertEqual(h0["recommendation"], "proceed_to_h0_source_os_foundation")

    def test_missing_ia_bundle_02_outputs_produce_blocked_partial_integration(self):
        entry = build_ia_source_cache_review_entry({"status": "not_created_blocked_by_policy"}, None)
        self.assertEqual(entry["review_integration_status"], "blocked_dry_run")

    def test_public_index_mutation_claim_is_rejected(self):
        entry = dict(self.source_entry)
        entry["truth_boundary"] = dict(entry["truth_boundary"])
        entry["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(detect_ia_review_truth_boundary_violations(entry, None))

    def test_master_index_mutation_claim_is_rejected(self):
        entry = dict(self.source_entry)
        entry["truth_boundary"] = dict(entry["truth_boundary"])
        entry["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(detect_ia_review_truth_boundary_violations(entry, None))

    def test_rights_malware_installability_claims_are_rejected(self):
        for key in ("rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"):
            with self.subTest(key=key):
                entry = dict(self.source_entry)
                entry["truth_boundary"] = dict(entry["truth_boundary"])
                entry["truth_boundary"][key] = True
                self.assertTrue(detect_ia_review_truth_boundary_violations(entry, None))

    def test_product_boundary_claim_is_rejected(self):
        entry = dict(self.source_entry)
        entry["product_boundary"] = dict(entry["product_boundary"])
        entry["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_ia_review_product_boundary_violations(entry, None))

    def test_runtime_does_not_call_model_provider(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in RUNTIME_FILES)
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))


if __name__ == "__main__":
    unittest.main()
