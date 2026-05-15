from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LocalLanSmokePolicyTests(unittest.TestCase):
    def test_lan_smoke_policy_requires_explicit_read_only_bind(self) -> None:
        policy = json.loads((ROOT / "control/policies/local_lan_smoke_policy.json").read_text(encoding="utf-8"))
        self.assertEqual("local_lan_smoke_policy.v0", policy["schema_version"])
        self.assertTrue(policy["bind_lan_required"])
        self.assertTrue(policy["read_only_required"])
        self.assertTrue(policy["same_machine_lan_bind_smoke_allowed"])
        self.assertTrue(policy["false_cross_device_claim_forbidden"])
        self.assertTrue(policy["no_deployment"])

    def test_external_client_policy_allows_not_performed_with_reason(self) -> None:
        policy = json.loads((ROOT / "control/policies/local_lan_external_client_evidence_policy.json").read_text(encoding="utf-8"))
        evidence = json.loads((ROOT / "control/inventory/local_lan_external_client_evidence.json").read_text(encoding="utf-8"))
        self.assertTrue(policy["external_client_optional_for_pass_with_warnings"])
        self.assertFalse(evidence["external_client_smoke_performed"])
        self.assertEqual("not_performed", evidence["status"])
        self.assertTrue(evidence["reason"])


if __name__ == "__main__":
    unittest.main()
