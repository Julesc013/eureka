from __future__ import annotations

import copy
from pathlib import Path
import unittest

from scripts import validate_h6_web_archive_news_event_policy_packs as validator


ROOT = Path(__file__).resolve().parents[2]


class H6WebArchiveNewsEventPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo(ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])
        self.assertEqual(result["source_count"], 13)

    def test_all_expected_examples_exist(self) -> None:
        for paths in validator.EXPECTED_SOURCES.values():
            for rel in paths.values():
                self.assertTrue((ROOT / rel).exists(), rel)

    def test_source_records_reject_enabled_behaviors(self) -> None:
        sample = _load_json("examples/sources/source_records/wayback_cdx_memento_source_v2.json")
        known = _known()
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "cdx_query_enabled",
            "memento_lookup_enabled",
            "warc_wacz_fetch_enabled",
            "archived_page_fetch_enabled",
            "media_download_enabled",
            "public_document_fetch_enabled",
            "scraping_enabled",
            "crawling_enabled",
            "bypass_or_automation_enabled",
        ):
            mutated = copy.deepcopy(sample)
            mutated[key] = True
            errors = validator.validate_source_record("wayback_cdx_memento", mutated, known)
            self.assertTrue(any(key in error for error in errors), key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        sample = _load_json("examples/connectors/h6_web_archive_news_event/policies/common_crawl_cdxj_policy_pack_v0.json")
        sample["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("common_crawl_cdxj", sample)
        self.assertTrue(any("policy_pack_grants_live_access" in error for error in errors))

    def test_coverage_overclaims_fail(self) -> None:
        sample = _load_json("examples/connectors/h6_web_archive_news_event/coverage/gdelt_news_event_coverage_preview_v0.json")
        sample["coverage_manifest_is_exhaustive_global_coverage"] = True
        errors = validator.validate_coverage_preview("gdelt_news_event", sample)
        self.assertTrue(any("coverage_manifest_is_exhaustive_global_coverage" in error for error in errors))

    def test_scorecard_overclaims_fail(self) -> None:
        sample = _load_json("examples/connectors/h6_web_archive_news_event/scorecards/trove_newspapers_scorecard_preview_v0.json")
        sample["production_ready"] = True
        errors = validator.validate_scorecard_preview("trove_newspapers", sample)
        self.assertTrue(any("production_ready" in error for error in errors))
        sample = _load_json("examples/connectors/h6_web_archive_news_event/scorecards/trove_newspapers_scorecard_preview_v0.json")
        sample["auto_approves_future_connectors"] = True
        errors = validator.validate_scorecard_preview("trove_newspapers", sample)
        self.assertTrue(any("auto_approves_future_connectors" in error for error in errors))

    def test_truth_boundary_overclaims_fail(self) -> None:
        sample = _load_json("examples/sources/source_records/cspan_video_library_source_v2.json")
        known = _known()
        for key in (
            "public_index_mutated",
            "master_index_mutated",
            "rights_clearance_claimed",
            "privacy_safety_claimed",
            "malware_safety_claimed",
            "verified_authenticity_claimed",
            "event_truth_accepted",
            "capture_record_is_complete",
        ):
            mutated = copy.deepcopy(sample)
            mutated.setdefault("truth_boundary", {})[key] = True
            errors = validator.validate_source_record("cspan_video_library", mutated, known)
            self.assertTrue(any(key in error for error in errors), key)

    def test_sensitive_or_payload_keys_are_rejected(self) -> None:
        errors: list[str] = []
        validator._scan_json_payload("sample.json", {"api_token": "x"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("sample.json", {"warc_payload": "not allowed"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("sample.json", {"scraping_output": "not allowed"}, errors)
        self.assertTrue(errors)

    def test_validator_does_not_create_private_roots(self) -> None:
        validator.validate_repo(ROOT)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka", "crawl_cache", "warc_wacz_cache", "media_downloads"):
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
