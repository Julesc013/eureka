from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from runtime.actions import action_manifest, action_policy, blocked_action
from runtime.actions.compare_manifest import build_compare_action_manifest, validate_compare_action_manifest


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class SafeActionManifestTests(unittest.TestCase):
    def test_view_action_manifest_builds(self) -> None:
        subject = load_json("examples/actions/manifests/view_action_manifest_v0.json")
        manifest = action_manifest.build_action_manifest(subject, "view")
        self.assertEqual(manifest["action_family"], "view")
        self.assertEqual(manifest["action_status"], "manifest_only")
        self.assertFalse(manifest["truth_boundary"]["action_manifest_executes_action"])
        self.assertEqual(action_manifest.validate_action_manifest(manifest), [])

    def test_inspect_action_manifest_builds(self) -> None:
        manifest = action_manifest.build_action_manifest(load_json("examples/actions/manifests/inspect_action_manifest_v0.json"), "inspect")
        self.assertEqual(manifest["action_family"], "inspect")
        self.assertIn("local_record_inspection_preview", manifest["allowed_effects"])

    def test_compare_action_manifest_builds_and_preserves_conflicts(self) -> None:
        manifest = build_compare_action_manifest([
            {"subject_ref": "candidate.one.v0"},
            {"subject_ref": "candidate.two.v0"},
        ])
        self.assertTrue(manifest["conflicts_preserved"])
        self.assertFalse(manifest["merge_allowed_current"])
        self.assertEqual(validate_compare_action_manifest(manifest), [])

    def test_cite_export_acquisition_preservation_manifest_actions_build(self) -> None:
        for family in ("cite", "export", "acquisition_manifest", "preserve_manifest"):
            with self.subTest(family=family):
                manifest = action_manifest.build_action_manifest({"subject_ref": f"{family}.subject.v0"}, family)
                self.assertEqual(manifest["action_status"], "manifest_only")
                self.assertFalse(manifest["truth_boundary"]["action_manifest_executes_action"])

    def test_risky_actions_are_blocked(self) -> None:
        for family in ("download", "mirror", "install", "execute", "emulate"):
            with self.subTest(family=family):
                manifest = action_manifest.build_action_manifest({"subject_ref": "subject.v0"}, family)
                self.assertEqual(manifest["action_status"], "blocked_by_policy")
                self.assertIn("blocked_action_report", manifest["generated_outputs"])

    def test_blocked_action_report_includes_reason_and_alternatives(self) -> None:
        report = blocked_action.build_download_blocked_report({"subject_ref": "source.v0"})
        self.assertIn("disabled", report["blocked_reason"])
        self.assertIn("view", report["safe_alternative_actions"])
        self.assertEqual(blocked_action.validate_blocked_action_report(report), [])

    def test_public_index_mutation_claim_is_rejected(self) -> None:
        manifest = action_manifest.build_action_manifest({"subject_ref": "subject.v0"}, "view")
        bad = copy.deepcopy(manifest)
        bad["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(any("public_index_mutated" in error for error in action_manifest.validate_action_manifest(bad)))

    def test_master_index_mutation_claim_is_rejected(self) -> None:
        manifest = action_manifest.build_action_manifest({"subject_ref": "subject.v0"}, "view")
        bad = copy.deepcopy(manifest)
        bad["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(any("master_index_mutated" in error for error in action_manifest.validate_action_manifest(bad)))

    def test_acceptance_and_rights_risk_claims_are_rejected(self) -> None:
        manifest = action_manifest.build_action_manifest({"subject_ref": "subject.v0"}, "view")
        for field in ("accepted_evidence", "accepted_candidate", "rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"):
            bad = copy.deepcopy(manifest)
            bad["truth_boundary"][field] = True
            self.assertTrue(any(field in error for error in action_manifest.validate_action_manifest(bad)))

    def test_validate_action_allowed_distinguishes_safe_and_risky(self) -> None:
        allowed, reasons = action_policy.validate_action_allowed("view")
        self.assertTrue(allowed)
        self.assertEqual(reasons, [])
        allowed, reasons = action_policy.validate_action_allowed("download")
        self.assertFalse(allowed)
        self.assertTrue(reasons)


if __name__ == "__main__":
    unittest.main()
