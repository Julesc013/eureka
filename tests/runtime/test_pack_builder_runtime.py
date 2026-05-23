import ast
import copy
import json
from pathlib import Path
import unittest

from runtime.local.foundry import pack_builder


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(path):
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


class PackBuilderRuntimeTest(unittest.TestCase):
    def test_source_pack_draft_builds_from_source_cache_record(self):
        record = load_json("examples/sources/cache/records/source_metadata_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "source_pack_draft")
        self.assertEqual(pack["pack_type"], "source_pack_draft")
        self.assertEqual(pack["pack_status"], "drafted_local")
        self.assertEqual(pack_builder.validate_pack_draft(pack), [])

    def test_evidence_pack_draft_builds_from_evidence_record(self):
        record = load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "evidence_pack_draft")
        self.assertEqual(pack["pack_type"], "evidence_pack_draft")
        self.assertEqual(pack["input_record_summary"]["input_type_counts"]["evidence_ledger_record"], 1)
        self.assertEqual(pack_builder.validate_pack_draft(pack), [])

    def test_contribution_pack_draft_builds_from_candidate_and_review(self):
        candidate = load_json("examples/index/candidates/search_need_candidate_v0.json")
        review = load_json("examples/review/queue_entries/candidate_needs_review_v0.json")
        pack = pack_builder.build_pack_draft([candidate, review], "contribution_pack_draft")
        self.assertEqual(pack["pack_type"], "contribution_pack_draft")
        self.assertEqual(pack["candidate_summary"]["candidate_ref_count"], 1)
        self.assertFalse(pack["truth_boundary"]["pack_draft_is_accepted_pack"])

    def test_review_pack_draft_builds_from_review_queue_entry(self):
        review = load_json("examples/review/queue_entries/candidate_needs_review_v0.json")
        pack = pack_builder.build_pack_draft([review], "review_pack_draft")
        self.assertEqual(pack["pack_type"], "review_pack_draft")
        self.assertEqual(pack["input_record_summary"]["input_type_counts"]["local_review_queue_entry"], 1)

    def test_index_pack_preview_remains_preview_only(self):
        proposal = load_json("examples/index/reviewed_public_records/minimal_reviewed_public_record_proposal_v0.json")
        pack = pack_builder.build_pack_draft([proposal], "index_pack_preview")
        self.assertEqual(pack["pack_status"], "validate_only")
        self.assertFalse(pack["pack_contents"]["public_index_mutation"])
        self.assertFalse(pack["truth_boundary"]["pack_draft_can_mutate_public_index"])

    def test_policy_blocked_pack_case_remains_blocked(self):
        record = load_json("examples/evidence/ledger/records/policy_blocked_evidence_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "policy_blocked_pack")
        self.assertEqual(pack["pack_status"], "policy_blocked")
        self.assertFalse(pack["truth_boundary"]["pack_draft_is_accepted_pack"])

    def test_submitted_or_accepted_pack_status_is_rejected(self):
        record = load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "evidence_pack_draft")
        pack["pack_status"] = "submitted_future"
        self.assertTrue(any("future-only" in error or "current runtime" in error for error in pack_builder.validate_pack_draft(pack)))
        pack["pack_status"] = "accepted_public_future"
        self.assertTrue(any("future-only" in error or "current runtime" in error for error in pack_builder.validate_pack_draft(pack)))

    def test_import_and_hosted_submission_claims_are_rejected(self):
        record = load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "evidence_pack_draft")
        imported = copy.deepcopy(pack)
        imported["pack_contents"]["imported_state"] = True
        self.assertTrue(any("imported_state" in error for error in pack_builder.validate_pack_draft(imported)))
        hosted = copy.deepcopy(pack)
        hosted["product_boundary"]["implemented_hosted_upload_runtime"] = True
        self.assertTrue(any("implemented_hosted_upload_runtime" in error for error in pack_builder.validate_pack_draft(hosted)))

    def test_evidence_and_index_mutation_claims_are_rejected(self):
        record = load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "evidence_pack_draft")
        for field in (
            "pack_draft_is_accepted_evidence",
            "pack_draft_can_mutate_public_index",
            "pack_draft_can_mutate_master_index",
        ):
            bad = copy.deepcopy(pack)
            bad["truth_boundary"][field] = True
            self.assertTrue(any(field in error for error in pack_builder.validate_pack_draft(bad)))

    def test_rights_malware_installability_and_exhaustive_claims_are_rejected(self):
        record = load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "evidence_pack_draft")
        for field in (
            "pack_draft_can_claim_rights_clearance",
            "pack_draft_can_claim_malware_safety",
            "pack_draft_can_claim_verified_installability",
            "pack_draft_can_claim_exhaustive_global_search",
        ):
            bad = copy.deepcopy(pack)
            bad["truth_boundary"][field] = True
            self.assertTrue(any(field in error for error in pack_builder.validate_pack_draft(bad)))

    def test_forbidden_input_type_is_rejected(self):
        errors = pack_builder.detect_forbidden_pack_input(
            [{"schema_version": "fixture.v0", "input_type": "secret_or_credential", "summary": "fixture"}]
        )
        self.assertTrue(any("secret_or_credential" in error for error in errors))

    def test_product_boundary_true_claim_fails(self):
        record = load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")
        pack = pack_builder.build_pack_draft([record], "evidence_pack_draft")
        pack["product_boundary"]["mutated_master_index"] = True
        self.assertTrue(any("mutated_master_index" in error for error in pack_builder.validate_pack_draft(pack)))

    def test_runtime_has_no_network_or_model_imports(self):
        tree = ast.parse((REPO_ROOT / "runtime/local/foundry/pack_builder.py").read_text(encoding="utf-8"))
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
