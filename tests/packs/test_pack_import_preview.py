from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from runtime.local_foundry import contribution_review, pack_import_preview, pack_quarantine


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class PackImportPreviewTests(unittest.TestCase):
    def test_import_preview_does_not_import(self) -> None:
        bundle = pack_quarantine.build_full_quarantine_bundle(load_json("examples/pack_exports/evidence_pack_export_v0.json"))
        preview = bundle["import_preview"]
        self.assertEqual(pack_import_preview.validate_pack_import_preview(preview), [])
        self.assertFalse(preview["truth_boundary"]["import_preview_imports_records"])
        self.assertIn("pack_import", preview["forbidden_effects"])

    def test_import_preview_projects_source_records(self) -> None:
        bundle = pack_quarantine.build_full_quarantine_bundle(load_json("examples/pack_exports/source_pack_export_v0.json"))
        preview = bundle["import_preview"]
        self.assertGreaterEqual(len(preview["proposed_source_records"]), 1)
        self.assertFalse(preview["proposed_source_records"][0]["imported"])

    def test_contribution_review_seed_is_not_review_decision(self) -> None:
        seed = pack_quarantine.build_full_quarantine_bundle(load_json("examples/pack_exports/contribution_pack_export_v0.json"))["contribution_review_seed"]
        self.assertFalse(seed["truth_boundary"]["review_seed_is_review_decision"])
        self.assertFalse(seed["proposed_review_entry"]["review_decision_created"])
        self.assertEqual(contribution_review.validate_contribution_review_seed(seed), [])

    def test_trust_preview_does_not_create_trust(self) -> None:
        preview = pack_quarantine.build_full_quarantine_bundle(load_json("examples/pack_exports/evidence_pack_export_v0.json"))["trust_preview"]
        self.assertEqual(preview["trust_status"], "preview_only_no_trust_created")
        self.assertFalse(preview["truth_boundary"]["trust_preview_creates_trust"])
        self.assertEqual(contribution_review.validate_pack_trust_preview(preview), [])

    def test_revocation_preview_does_not_revoke(self) -> None:
        preview = pack_quarantine.build_full_quarantine_bundle(load_json("examples/pack_exports/policy_blocked_pack_export_v0.json"))["revocation_preview"]
        self.assertEqual(preview["revocation_status"], "preview_only_no_revocation")
        self.assertFalse(preview["truth_boundary"]["revocation_preview_revokes_pack"])

    def test_import_preview_acceptance_claim_is_rejected(self) -> None:
        preview = pack_quarantine.build_full_quarantine_bundle(load_json("examples/pack_exports/evidence_pack_export_v0.json"))["import_preview"]
        bad = copy.deepcopy(preview)
        bad["truth_boundary"]["accepted_candidate"] = True
        self.assertTrue(any("accepted_candidate" in error for error in pack_import_preview.validate_pack_import_preview(bad)))


if __name__ == "__main__":
    unittest.main()
