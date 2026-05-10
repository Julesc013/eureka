from __future__ import annotations

import copy
from pathlib import Path
import unittest

from scripts import validate_h5_vendor_update_driver_policy_packs as validator


ROOT = Path(__file__).resolve().parents[2]


class H5VendorUpdateDriverPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo(ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])
        self.assertEqual(result["source_count"], 15)

    def test_all_expected_examples_exist(self) -> None:
        for paths in validator.EXPECTED_SOURCES.values():
            for rel in paths.values():
                self.assertTrue((ROOT / rel).exists(), rel)

    def test_source_records_reject_enabled_behaviors(self) -> None:
        sample = _load_json("examples/sources/source_records/microsoft_update_catalog_source_v2.json")
        known = _known()
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "vendor_catalog_fetch_enabled",
            "driver_download_enabled",
            "firmware_download_enabled",
            "runtime_download_enabled",
            "installer_download_enabled",
            "vendor_tool_invocation_enabled",
            "firmware_flash_enabled",
            "install_execute_enabled",
        ):
            mutated = copy.deepcopy(sample)
            mutated[key] = True
            errors = validator.validate_source_record("microsoft_update_catalog", mutated, known)
            self.assertTrue(any(key in error for error in errors), key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        sample = _load_json("examples/connectors/h5_vendor_update_driver/policies/nvidia_driver_downloads_policy_pack_v0.json")
        sample["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("nvidia_driver_downloads", sample)
        self.assertTrue(any("policy_pack_grants_live_access" in error for error in errors))

    def test_coverage_overclaims_fail(self) -> None:
        sample = _load_json("examples/connectors/h5_vendor_update_driver/coverage/amd_driver_downloads_coverage_preview_v0.json")
        sample["coverage_manifest_is_exhaustive_global_coverage"] = True
        errors = validator.validate_coverage_preview("amd_driver_downloads", sample)
        self.assertTrue(any("coverage_manifest_is_exhaustive_global_coverage" in error for error in errors))

    def test_scorecard_overclaims_fail(self) -> None:
        sample = _load_json("examples/connectors/h5_vendor_update_driver/scorecards/intel_driver_support_scorecard_preview_v0.json")
        sample["production_ready"] = True
        errors = validator.validate_scorecard_preview("intel_driver_support", sample)
        self.assertTrue(any("production_ready" in error for error in errors))
        sample = _load_json("examples/connectors/h5_vendor_update_driver/scorecards/intel_driver_support_scorecard_preview_v0.json")
        sample["auto_approves_future_connectors"] = True
        errors = validator.validate_scorecard_preview("intel_driver_support", sample)
        self.assertTrue(any("auto_approves_future_connectors" in error for error in errors))

    def test_truth_boundary_overclaims_fail(self) -> None:
        sample = _load_json("examples/sources/source_records/dell_support_downloads_source_v2.json")
        known = _known()
        for key in (
            "public_index_mutated",
            "master_index_mutated",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "verified_installability_claimed",
            "verified_compatibility_claimed",
            "verified_authenticity_claimed",
            "accepted_vendor_truth",
            "accepted_driver_identity",
            "accepted_firmware_identity",
            "accepted_runtime_identity",
            "accepted_compatibility_truth",
            "accepted_authenticity_truth",
            "accepted_safety_truth",
        ):
            mutated = copy.deepcopy(sample)
            mutated.setdefault("truth_boundary", {})[key] = True
            errors = validator.validate_source_record("dell_support_downloads", mutated, known)
            self.assertTrue(any(key in error for error in errors), key)

    def test_sensitive_or_payload_keys_are_rejected(self) -> None:
        errors: list[str] = []
        validator._scan_json_payload("sample.json", {"api_token": "x"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("sample.json", {"firmware_image": "not allowed"}, errors)
        self.assertTrue(errors)

    def test_validator_does_not_create_private_roots(self) -> None:
        validator.validate_repo(ROOT)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka", "vendor_downloads", "firmware_staging", "package_cache"):
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
