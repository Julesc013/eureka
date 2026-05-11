from __future__ import annotations

import unittest

from runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture
from runtime.connectors.h13_local_private import rights_sensitive_source_policy_blocked
from scripts import validate_h13_local_private_fixture_runtime as validator


class H13RightsSafetyMappingTests(unittest.TestCase):
    def test_rights_safety_candidate_is_not_clearance_or_safety(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/rights_sensitive_source_policy_blocked/rights_safety_record.json")
        candidate = rights_sensitive_source_policy_blocked.normalize(fixture)["local_private_rights_safety_candidate"]
        truth = candidate["truth_boundary"]
        self.assertFalse(truth["local_private_rights_safety_candidate_is_rights_or_safety_truth"])
        self.assertFalse(truth["rights_clearance_claimed"])
        self.assertFalse(truth["legal_access_claimed"])
        self.assertFalse(truth["privacy_safety_claimed"])
        self.assertFalse(truth["malware_safety_claimed"])
        self.assertFalse(truth["source_safety_claimed"])


if __name__ == "__main__":
    unittest.main()
