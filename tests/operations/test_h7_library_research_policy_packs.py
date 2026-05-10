from __future__ import annotations

import copy
from pathlib import Path
import unittest

from scripts import validate_h7_library_research_policy_packs as validator


ROOT = Path(__file__).resolve().parents[2]


class H7LibraryResearchPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo(ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])
        self.assertEqual(result["source_count"], 30)

    def test_all_expected_examples_exist(self) -> None:
        for paths in validator.EXPECTED_SOURCES.values():
            for rel in paths.values():
                self.assertTrue((ROOT / rel).exists(), rel)

    def test_source_records_reject_enabled_behaviors(self) -> None:
        sample = _load_json("examples/sources/source_records/worldcat_library_catalog_source_v2.json")
        known = _known()
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "oai_pmh_harvest_enabled",
            "api_query_enabled",
            "full_text_fetch_enabled",
            "pdf_download_enabled",
            "dataset_download_enabled",
            "patent_document_download_enabled",
            "scraping_enabled",
            "crawling_enabled",
            "bypass_or_automation_enabled",
        ):
            mutated = copy.deepcopy(sample)
            mutated[key] = True
            errors = validator.validate_source_record("worldcat_library_catalog", mutated, known)
            self.assertTrue(any(key in error for error in errors), key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        sample = _load_json("examples/connectors/h7_library_research/policies/openalex_policy_pack_v0.json")
        sample["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("openalex", sample)
        self.assertTrue(any("policy_pack_grants_live_access" in error for error in errors))

    def test_coverage_overclaims_fail(self) -> None:
        sample = _load_json("examples/connectors/h7_library_research/coverage/h7_library_research_coverage_preview_v0.json")
        sample["coverage_manifest_is_exhaustive_global_coverage"] = True
        errors = validator.validate_coverage_preview(sample)
        self.assertTrue(any("coverage_manifest_is_exhaustive_global_coverage" in error for error in errors))

    def test_scorecard_overclaims_fail(self) -> None:
        sample = _load_json("examples/connectors/h7_library_research/scorecards/h7_library_research_scorecard_preview_v0.json")
        sample["production_ready"] = True
        errors = validator.validate_scorecard_preview(sample)
        self.assertTrue(any("production_ready" in error for error in errors))
        sample = _load_json("examples/connectors/h7_library_research/scorecards/h7_library_research_scorecard_preview_v0.json")
        sample["auto_approves_future_connectors"] = True
        errors = validator.validate_scorecard_preview(sample)
        self.assertTrue(any("auto_approves_future_connectors" in error for error in errors))

    def test_truth_boundary_overclaims_fail(self) -> None:
        sample = _load_json("examples/sources/source_records/datacite_source_v2.json")
        known = _known()
        for key in (
            "public_index_mutated",
            "master_index_mutated",
            "accepted_bibliographic_truth",
            "accepted_research_work_truth",
            "accepted_dataset_truth",
            "accepted_cultural_object_truth",
            "accepted_patent_truth",
            "accepted_citation_truth",
            "accepted_access_rights_truth",
            "rights_clearance_claimed",
            "privacy_safety_claimed",
            "malware_safety_claimed",
            "verified_availability_claimed",
        ):
            mutated = copy.deepcopy(sample)
            mutated.setdefault("truth_boundary", {})[key] = True
            errors = validator.validate_source_record("datacite", mutated, known)
            self.assertTrue(any(key in error for error in errors), key)

    def test_sensitive_or_payload_keys_are_rejected(self) -> None:
        errors: list[str] = []
        validator._scan_json_payload("sample.json", {"api_token": "x"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("sample.json", {"pdf_payload": "not allowed"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("sample.json", {"dataset_payload": "not allowed"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("sample.json", {"scraping_output": "not allowed"}, errors)
        self.assertTrue(errors)

    def test_validator_does_not_create_private_roots(self) -> None:
        validator.validate_repo(ROOT)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka", "harvest_cache", "pdf_downloads", "book_downloads", "article_downloads", "dataset_downloads", "ocr_cache", "media_downloads"):
            self.assertFalse((ROOT / rel).exists(), rel)


def _load_json(rel: str) -> dict:
    import json

    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _known() -> dict[str, set[str]]:
    errors: list[str] = []
    known = validator._load_known_values(ROOT, errors)
    assert not errors
    return known


if __name__ == "__main__":
    unittest.main()
