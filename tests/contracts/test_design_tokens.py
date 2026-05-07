from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from scripts.validate_design_tokens import (
    EXAMPLE_PATHS,
    REPO_ROOT,
    TOKEN_INVENTORY_PATH,
    validate_design_token_payload,
    validate_design_tokens,
)


SITE_DIST = REPO_ROOT / "site" / "dist"


def load_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def site_dist_hashes() -> dict[str, str]:
    return {
        path.as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(SITE_DIST.rglob("*"))
        if path.is_file()
    }


class DesignTokensContractTest(unittest.TestCase):
    def test_valid_token_examples_pass(self) -> None:
        report = validate_design_tokens(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["examples"], EXAMPLE_PATHS)

    def test_token_inventory_passes(self) -> None:
        errors = validate_design_token_payload(load_json(TOKEN_INVENTORY_PATH), TOKEN_INVENTORY_PATH)

        self.assertEqual(errors, [])

    def test_missing_required_token_family_fails(self) -> None:
        payload = load_json("examples/design_tokens/minimal_design_tokens_v0.json")
        del payload["color_tokens"]

        errors = validate_design_token_payload(payload, "fixture.json")

        self.assertTrue(any("missing required field color_tokens" in error for error in errors))

    def test_hosted_live_download_upload_account_telemetry_claim_fails(self) -> None:
        payload = load_json("examples/design_tokens/minimal_design_tokens_v0.json")
        payload["product_boundary"]["enabled_hosting"] = True
        payload["product_boundary"]["enabled_live_probes"] = True
        payload["product_boundary"]["enabled_downloads"] = True
        payload["product_boundary"]["enabled_uploads"] = True
        payload["product_boundary"]["enabled_accounts"] = True
        payload["product_boundary"]["enabled_telemetry"] = True

        errors = validate_design_token_payload(payload, "fixture.json")

        for field in (
            "enabled_hosting",
            "enabled_live_probes",
            "enabled_downloads",
            "enabled_uploads",
            "enabled_accounts",
            "enabled_telemetry",
        ):
            self.assertTrue(any(f"product_boundary.{field} must be false" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        payload = load_json("examples/design_tokens/minimal_design_tokens_v0.json")
        payload["product_boundary"]["copied_google_branding"] = True

        errors = validate_design_token_payload(payload, "fixture.json")

        self.assertTrue(any("product_boundary.copied_google_branding must be false" in error for error in errors))

    def test_validator_does_not_mutate_site_dist(self) -> None:
        before = site_dist_hashes()

        report = validate_design_tokens(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(site_dist_hashes(), before)

    def test_payload_copy_with_text_product_claim_fails(self) -> None:
        payload = copy.deepcopy(load_json("examples/design_tokens/minimal_design_tokens_v0.json"))
        payload["notes"].append("hosted backend active")

        errors = validate_design_token_payload(payload, "fixture.json")

        self.assertTrue(any("unsafe product claim" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
