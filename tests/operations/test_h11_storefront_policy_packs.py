from __future__ import annotations

import copy
import unittest

from scripts import validate_h11_storefront_policy_packs as validator


class H11StorefrontPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_enablement_flags_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/microsoft_store_metadata_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "api_query_enabled",
            "catalog_fetch_enabled",
            "storefront_search_enabled",
            "product_page_fetch_enabled",
            "app_download_enabled",
            "package_download_enabled",
            "account_access_enabled",
            "purchase_automation_enabled",
            "entitlement_verification_enabled",
            "install_execute_enabled",
            "launch_execute_enabled",
            "review_rating_write_enabled",
            "scraping_enabled",
            "crawling_enabled",
            "bypass_or_automation_enabled",
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = True
            errors = validator.validate_source_record("microsoft_store_metadata", mutated, known)
            self.assertTrue(errors, key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        pack = validator._load_json(validator.REPO_ROOT / "examples/connectors/h11_storefront/policies/microsoft_store_metadata_policy_pack_v0.json")
        mutated = copy.deepcopy(pack)
        mutated["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("microsoft_store_metadata", mutated)
        self.assertTrue(errors)

    def test_preview_overclaims_fail(self) -> None:
        coverage = validator._load_json(validator.REPO_ROOT / "examples/connectors/h11_storefront/coverage/h11_storefront_coverage_preview_v0.json")
        coverage["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage))
        scorecard = validator._load_json(validator.REPO_ROOT / "examples/connectors/h11_storefront/scorecards/h11_storefront_scorecard_preview_v0.json")
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))
        scorecard["production_ready"] = False
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))

    def test_truth_and_payload_claims_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/microsoft_store_metadata_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "accepted_listing_identity_truth",
            "accepted_app_product_truth",
            "accepted_version_release_truth",
            "accepted_price_availability_truth",
            "accepted_acquisition_permission",
            "accepted_review_rating_truth",
            "accepted_account_entitlement_truth",
            "accepted_rights_safety_truth",
            "public_index_mutated",
            "master_index_mutated",
            "rights_clearance_claimed",
            "current_price_claimed",
            "current_availability_claimed",
            "license_entitlement_claimed",
            "legal_acquisition_claimed",
            "installability_claimed",
            "malware_safety_claimed",
            "content_safety_claimed",
            "privacy_safety_claimed",
            "verified_authenticity_claimed",
        ):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(validator.validate_source_record("microsoft_store_metadata", mutated, known), key)
        for payload_key in (
            "api_token",
            "receipt_payload",
            "payment_payload",
            "license_key_payload",
            "entitlement_payload",
            "app_package_payload",
            "installer_payload",
            "download_payload",
            "purchase_output",
            "checkout_output",
            "install_log",
            "launch_log",
            "scraping_output",
        ):
            errors: list[str] = []
            validator._scan_json_payload("synthetic", {payload_key: "not allowed"}, errors)
            self.assertTrue(errors, payload_key)


if __name__ == "__main__":
    unittest.main()
