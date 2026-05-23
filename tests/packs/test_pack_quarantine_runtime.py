from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from runtime.local.foundry import pack_quarantine


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class PackQuarantineRuntimeTests(unittest.TestCase):
    def test_exported_evidence_pack_can_be_quarantined(self) -> None:
        pack = load_json("examples/packs/exports/evidence_pack_export_v0.json")
        bundle = pack_quarantine.build_full_quarantine_bundle(pack)
        result = bundle["quarantine_result"]
        self.assertEqual(result["input_pack_type"], "evidence_pack_export")
        self.assertEqual(result["quarantine_status"], "quarantined_local")
        self.assertEqual(pack_quarantine.validate_pack_quarantine_result(result), [])

    def test_exported_source_pack_can_be_quarantined(self) -> None:
        pack = load_json("examples/packs/exports/source_pack_export_v0.json")
        result = pack_quarantine.build_full_quarantine_bundle(pack)["quarantine_result"]
        self.assertEqual(result["input_pack_type"], "source_pack_export")
        self.assertFalse(result["truth_boundary"]["quarantined_pack_is_imported"])

    def test_contribution_pack_can_be_quarantined(self) -> None:
        pack = load_json("examples/packs/exports/contribution_pack_export_v0.json")
        result = pack_quarantine.build_full_quarantine_bundle(pack)["quarantine_result"]
        self.assertEqual(result["input_pack_type"], "contribution_pack_export")
        self.assertIn("human_review", result["allowed_next_actions"])

    def test_policy_blocked_pack_remains_blocked(self) -> None:
        pack = load_json("examples/packs/exports/policy_blocked_pack_export_v0.json")
        result = pack_quarantine.build_full_quarantine_bundle(pack)["quarantine_result"]
        self.assertEqual(result["quarantine_status"], "blocked_by_policy")
        self.assertIn("policy_blocked_pack_export", result["blocker_summary"]["blockers"])

    def test_quarantine_result_is_not_accepted_imported_or_submitted(self) -> None:
        result = pack_quarantine.build_full_quarantine_bundle(load_json("examples/packs/exports/evidence_pack_export_v0.json"))["quarantine_result"]
        truth = result["truth_boundary"]
        self.assertFalse(truth["quarantined_pack_is_accepted"])
        self.assertFalse(truth["quarantined_pack_is_imported"])
        self.assertFalse(truth["quarantined_pack_is_submitted"])
        self.assertFalse(truth["public_index_mutated"])
        self.assertFalse(truth["master_index_mutated"])

    def test_public_index_mutation_claim_is_rejected(self) -> None:
        result = pack_quarantine.build_full_quarantine_bundle(load_json("examples/packs/exports/evidence_pack_export_v0.json"))["quarantine_result"]
        bad = copy.deepcopy(result)
        bad["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(any("public_index_mutated" in error for error in pack_quarantine.validate_pack_quarantine_result(bad)))

    def test_master_index_mutation_claim_is_rejected(self) -> None:
        result = pack_quarantine.build_full_quarantine_bundle(load_json("examples/packs/exports/evidence_pack_export_v0.json"))["quarantine_result"]
        bad = copy.deepcopy(result)
        bad["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(any("master_index_mutated" in error for error in pack_quarantine.validate_pack_quarantine_result(bad)))

    def test_accepted_truth_claim_is_rejected(self) -> None:
        result = pack_quarantine.build_full_quarantine_bundle(load_json("examples/packs/exports/evidence_pack_export_v0.json"))["quarantine_result"]
        bad = copy.deepcopy(result)
        bad["truth_boundary"]["accepted_evidence"] = True
        self.assertTrue(any("accepted_evidence" in error for error in pack_quarantine.validate_pack_quarantine_result(bad)))

    def test_rights_malware_installability_claims_are_rejected(self) -> None:
        result = pack_quarantine.build_full_quarantine_bundle(load_json("examples/packs/exports/evidence_pack_export_v0.json"))["quarantine_result"]
        for field in ("rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"):
            bad = copy.deepcopy(result)
            bad["truth_boundary"][field] = True
            self.assertTrue(any(field in error for error in pack_quarantine.validate_pack_quarantine_result(bad)))


if __name__ == "__main__":
    unittest.main()
