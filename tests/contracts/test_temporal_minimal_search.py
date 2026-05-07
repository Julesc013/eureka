from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from scripts.validate_temporal_minimal_search import (
    DESIGN_LANGUAGE_EXAMPLE,
    PROFILE_MATRIX,
    REPO_ROOT,
    validate_design_profile_matrix,
    validate_temporal_minimal_search,
    validate_temporal_payload,
)
from scripts.validate_track_a_contracts import validate_track_a_contracts


SITE_DIST = REPO_ROOT / "site" / "dist"
REPRESENTATION_IDS = {
    "api_json",
    "file_tree",
    "html32",
    "lite_html",
    "manifest_json",
    "native_card_future",
    "print",
    "relay_future",
    "snapshot_future",
    "standard_html",
    "terminal_future",
    "text",
}


def load_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def site_dist_hashes() -> dict[str, str]:
    return {
        path.as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(SITE_DIST.rglob("*"))
        if path.is_file()
    }


class TemporalMinimalSearchContractTest(unittest.TestCase):
    def test_valid_temporal_minimal_search_example_passes(self) -> None:
        report = validate_temporal_minimal_search(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_missing_semantic_visibility_requirement_fails(self) -> None:
        payload = load_json(DESIGN_LANGUAGE_EXAMPLE)
        payload["required_semantic_visibility"].remove("source_posture")

        errors = validate_temporal_payload(payload, "fixture.json")

        self.assertTrue(any("required_semantic_visibility missing source_posture" in error for error in errors))

    def test_missing_forbidden_branding_rule_fails(self) -> None:
        payload = load_json(DESIGN_LANGUAGE_EXAMPLE)
        payload["forbidden_branding_or_trade_dress"].remove("no_google_logos")

        errors = validate_temporal_payload(payload, "fixture.json")

        self.assertTrue(any("forbidden_branding_or_trade_dress missing no_google_logos" in error for error in errors))

    def test_google_branding_affiliation_claim_fails(self) -> None:
        payload = copy.deepcopy(load_json(DESIGN_LANGUAGE_EXAMPLE))
        payload["notes"].append("Affiliated with Google Search.")

        errors = validate_temporal_payload(payload, "fixture.json")

        self.assertTrue(any("unsafe branding or affiliation claim" in error for error in errors))

    def test_invalid_representation_profile_reference_fails(self) -> None:
        matrix = load_json(PROFILE_MATRIX)
        matrix["profiles"][0]["intended_representation_profiles"].append("invalid_profile")

        errors = validate_design_profile_matrix(matrix, "fixture.json", REPRESENTATION_IDS)

        self.assertTrue(any("unknown representation profile invalid_profile" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        matrix = load_json(PROFILE_MATRIX)
        matrix["product_boundary"]["enabled_hosting"] = True

        errors = validate_design_profile_matrix(matrix, "fixture.json", REPRESENTATION_IDS)

        self.assertTrue(any("product_boundary.enabled_hosting must be false" in error for error in errors))

    def test_validator_does_not_mutate_site_dist(self) -> None:
        before = site_dist_hashes()

        report = validate_temporal_minimal_search(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(site_dist_hashes(), before)

    def test_cross_validator_includes_temporal_contracts(self) -> None:
        report = validate_track_a_contracts(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["validator_count"], 12)
        self.assertTrue(any(group["group_id"] == "temporal_minimal_search" for group in report["groups"]))


if __name__ == "__main__":
    unittest.main()
