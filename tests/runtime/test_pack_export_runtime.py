import ast
import copy
import json
from pathlib import Path
import unittest

from runtime.local.foundry import pack_export


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(path):
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


class PackExportRuntimeTest(unittest.TestCase):
    def test_source_pack_draft_exports_to_source_pack_export(self):
        draft = load_json("examples/packs/drafts/source_pack_draft_v0.json")
        export = pack_export.build_pack_export(draft)
        self.assertEqual(export["export_pack_type"], "source_pack_export")
        self.assertEqual(export["export_status"], "exported_local")
        self.assertEqual(pack_export.validate_pack_export(export), [])

    def test_evidence_pack_draft_exports_to_evidence_pack_export(self):
        draft = load_json("examples/packs/drafts/evidence_pack_draft_v0.json")
        export = pack_export.build_pack_export(draft)
        self.assertEqual(export["export_pack_type"], "evidence_pack_export")
        self.assertEqual(export["fixity"]["algorithm"], "sha256")
        self.assertEqual(pack_export.validate_pack_export(export), [])

    def test_contribution_and_review_pack_exports(self):
        contribution = pack_export.build_pack_export(load_json("examples/packs/drafts/contribution_pack_draft_v0.json"))
        review = pack_export.build_pack_export(load_json("examples/packs/drafts/review_pack_draft_v0.json"))
        self.assertEqual(contribution["export_pack_type"], "contribution_pack_export")
        self.assertEqual(review["export_pack_type"], "review_pack_export")

    def test_index_pack_preview_exports_as_preview_only(self):
        export = pack_export.build_pack_export(load_json("examples/packs/drafts/index_pack_preview_v0.json"))
        self.assertEqual(export["export_pack_type"], "index_pack_preview_export")
        self.assertEqual(export["export_status"], "validate_only")
        self.assertFalse(export["truth_boundary"]["exported_pack_can_mutate_public_index"])

    def test_policy_blocked_pack_export_remains_blocked(self):
        export = pack_export.build_pack_export(load_json("examples/packs/drafts/policy_blocked_pack_draft_v0.json"))
        self.assertEqual(export["export_pack_type"], "policy_blocked_pack_export")
        self.assertEqual(export["export_status"], "policy_blocked")

    def test_exported_pack_is_not_accepted_submitted_or_imported(self):
        export = pack_export.build_pack_export(load_json("examples/packs/drafts/evidence_pack_draft_v0.json"))
        metadata = export["exported_pack"]["export_metadata"]
        self.assertFalse(metadata["accepted"])
        self.assertFalse(metadata["submitted"])
        self.assertFalse(metadata["imported"])
        self.assertFalse(export["truth_boundary"]["exported_pack_is_accepted_pack"])

    def test_fixity_is_deterministic_sha256(self):
        draft = load_json("examples/packs/drafts/evidence_pack_draft_v0.json")
        first = pack_export.build_pack_export(draft)
        second = pack_export.build_pack_export(draft)
        self.assertEqual(first["fixity"]["sha256"], second["fixity"]["sha256"])
        self.assertEqual(len(first["fixity"]["sha256"]), 64)

    def test_real_signature_and_private_key_claims_are_rejected(self):
        export = pack_export.build_pack_export(load_json("examples/packs/drafts/evidence_pack_draft_v0.json"))
        signed = copy.deepcopy(export)
        signed["signature_policy"]["real_signing_enabled"] = True
        self.assertTrue(any("real_signing_enabled" in error for error in pack_export.validate_pack_export(signed)))
        private_key = copy.deepcopy(export)
        private_key["notes"].append("private key: fixture")
        self.assertTrue(any("private" in error.lower() or "credential" in error.lower() for error in pack_export.validate_pack_export(private_key)))

    def test_import_upload_acceptance_and_index_claims_are_rejected(self):
        export = pack_export.build_pack_export(load_json("examples/packs/drafts/evidence_pack_draft_v0.json"))
        for field in ("imported", "submitted", "hosted_upload", "accepted", "public_index_mutation", "master_index_mutation"):
            bad = copy.deepcopy(export)
            bad["exported_pack"]["export_metadata"][field] = True
            self.assertTrue(any(field in error for error in pack_export.validate_pack_export(bad)))

    def test_truth_boundary_claims_are_rejected(self):
        export = pack_export.build_pack_export(load_json("examples/packs/drafts/evidence_pack_draft_v0.json"))
        for field in (
            "exported_pack_is_accepted_evidence",
            "exported_pack_can_mutate_public_index",
            "exported_pack_can_mutate_master_index",
            "exported_pack_can_claim_rights_clearance",
            "exported_pack_can_claim_malware_safety",
            "exported_pack_can_claim_verified_installability",
            "exported_pack_can_claim_exhaustive_global_search",
        ):
            bad = copy.deepcopy(export)
            bad["truth_boundary"][field] = True
            self.assertTrue(any(field in error for error in pack_export.validate_pack_export(bad)))

    def test_product_boundary_true_claim_fails(self):
        export = pack_export.build_pack_export(load_json("examples/packs/drafts/evidence_pack_draft_v0.json"))
        export["product_boundary"]["mutated_master_index"] = True
        self.assertTrue(any("mutated_master_index" in error for error in pack_export.validate_pack_export(export)))

    def test_runtime_has_no_network_or_model_imports(self):
        tree = ast.parse((REPO_ROOT / "runtime/local/foundry/pack_export.py").read_text(encoding="utf-8"))
        banned = {"requests", "urllib", "http", "socket", "webbrowser", "openai"}
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertFalse(imports & banned)


if __name__ == "__main__":
    unittest.main()
