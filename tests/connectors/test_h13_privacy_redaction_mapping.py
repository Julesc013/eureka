from __future__ import annotations

import unittest

from archive.prototypes.legacy_runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture
from archive.prototypes.legacy_runtime.connectors.h13_local_private import local_folder_metadata
from archive.prototypes.legacy_runtime.connectors.h13_local_private.path_safety import is_public_safe_locator
from scripts import validate_h13_local_private_fixture_runtime as validator


class H13PrivacyRedactionMappingTests(unittest.TestCase):
    def test_privacy_candidate_does_not_prove_public_safety(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/local_folder_metadata/privacy_redaction_record.json")
        candidate = local_folder_metadata.normalize(fixture)["privacy_redaction_candidate"]
        self.assertFalse(candidate["truth_boundary"]["privacy_redaction_candidate_proves_public_safety"])

    def test_unrestricted_path_fixture_fails(self) -> None:
        errors: list[str] = []
        validator._scan_json_boundaries({"path": "C:\\Users\\Example\\private.bin"}, "synthetic", errors)
        self.assertTrue(errors)
        self.assertFalse(is_public_safe_locator("C:\\Users\\Example\\private.bin"))

    def test_secret_and_private_payload_keys_fail(self) -> None:
        for key in ("api_token", "session_cookie", "private_file_payload", "local_file_content", "cas_blob", "exported_pack", "source_cache_write", "public_index_write"):
            errors: list[str] = []
            validator._scan_json_boundaries({key: "not allowed"}, "synthetic", errors)
            self.assertTrue(errors, key)


if __name__ == "__main__":
    unittest.main()
