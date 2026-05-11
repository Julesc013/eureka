from __future__ import annotations

import copy
import json
import unittest

from scripts import validate_h8_manuals_docs_standards_policy_packs as validator


class H8ManualsDocsStandardsPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_enablement_flags_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/bitsavers_docs_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "api_query_enabled",
            "catalog_fetch_enabled",
            "document_download_enabled",
            "pdf_download_enabled",
            "full_text_fetch_enabled",
            "ocr_extraction_enabled",
            "standards_document_fetch_enabled",
            "scraping_enabled",
            "crawling_enabled",
            "bypass_or_automation_enabled",
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = True
            errors = validator.validate_source_record("bitsavers_docs", mutated, known)
            self.assertTrue(errors, key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        pack = validator._load_json(validator.REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/policies/bitsavers_docs_policy_pack_v0.json")
        mutated = copy.deepcopy(pack)
        mutated["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("bitsavers_docs", mutated)
        self.assertTrue(errors)

    def test_preview_overclaims_fail(self) -> None:
        coverage = validator._load_json(validator.REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/coverage/h8_manuals_docs_standards_coverage_preview_v0.json")
        coverage["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage))
        scorecard = validator._load_json(validator.REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/scorecards/h8_manuals_docs_standards_scorecard_preview_v0.json")
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))
        scorecard["production_ready"] = False
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))

    def test_truth_and_payload_claims_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/bitsavers_docs_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "accepted_document_truth",
            "accepted_manual_artifact_relation_truth",
            "accepted_datasheet_device_truth",
            "accepted_standard_truth",
            "accepted_install_requirement_truth",
            "accepted_repair_safety_truth",
            "accepted_access_rights_truth",
            "public_index_mutated",
            "master_index_mutated",
            "rights_clearance_claimed",
            "open_access_truth_claimed",
            "compatibility_correctness_claimed",
            "installability_claimed",
            "repair_safety_claimed",
            "electrical_safety_claimed",
        ):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(validator.validate_source_record("bitsavers_docs", mutated, known), key)
        errors: list[str] = []
        validator._scan_json_payload("synthetic", {"api_token": "secret"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("synthetic", {"pdf_payload": "not allowed"}, errors)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
