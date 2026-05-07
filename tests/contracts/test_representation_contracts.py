from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_representation_contracts import (
    validate_payloads,
    validate_representation_contracts,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict]:
    return (
        load_json(PUBLICATION_DIR / "host_profiles.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "capability_negotiation_policy.json"),
    )


class RepresentationContractsTest(unittest.TestCase):
    def test_valid_inventories_pass(self) -> None:
        report = validate_representation_contracts(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertGreaterEqual(report["inventory_host_profile_count"], 7)
        self.assertGreaterEqual(report["inventory_representation_profile_count"], 11)

    def test_broken_host_profile_reference_fails(self) -> None:
        hosts, representations, policy = load_payloads()
        hosts = copy.deepcopy(hosts)
        hosts["profiles"][0]["default_representation_profile"] = "missing_profile"
        hosts["profiles"][0]["allowed_representation_profiles"].append("missing_profile")
        policy = copy.deepcopy(policy)
        policy["host_profile_defaults"]["www_auto"] = "missing_profile"

        errors = validate_payloads(
            hosts,
            representations,
            policy,
            source_label="unit",
            require_inventory_ids=True,
        )

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_legacy_profile_with_auth_cookies_or_writes_fails(self) -> None:
        hosts, representations, policy = load_payloads()
        hosts = copy.deepcopy(hosts)
        for profile in hosts["profiles"]:
            if profile["host_profile_id"] == "old_legacy_read_only":
                profile["auth_allowed"] = True
                profile["cookie_allowed"] = True
                profile["write_actions_allowed"] = True
                break

        errors = validate_payloads(
            hosts,
            representations,
            policy,
            source_label="unit",
            require_inventory_ids=True,
        )

        self.assertTrue(
            any("legacy/http-compatible profile must not allow auth_allowed" in error for error in errors)
        )
        self.assertTrue(
            any("legacy/http-compatible profile must not allow cookie_allowed" in error for error in errors)
        )
        self.assertTrue(
            any("legacy/http-compatible profile must not allow write_actions_allowed" in error for error in errors)
        )

    def test_missing_semantic_requirements_fail(self) -> None:
        hosts, representations, policy = load_payloads()
        representations = copy.deepcopy(representations)
        representations["profiles"][0]["semantic_requirements"] = []

        errors = validate_payloads(
            hosts,
            representations,
            policy,
            source_label="unit",
            require_inventory_ids=True,
        )

        self.assertTrue(any("semantic_requirements" in error for error in errors))

    def test_missing_fallback_profile_fails(self) -> None:
        hosts, representations, policy = load_payloads()
        policy = copy.deepcopy(policy)
        policy["fallback_profile"] = "missing_profile"

        errors = validate_payloads(
            hosts,
            representations,
            policy,
            source_label="unit",
            require_inventory_ids=True,
        )

        self.assertTrue(any("fallback profile 'missing_profile'" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
