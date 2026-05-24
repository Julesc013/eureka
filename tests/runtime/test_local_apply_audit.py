from __future__ import annotations

import json
import unittest

from runtime.local.apply import APPLY_CONFIRMATION, run_local_apply
from tests.runtime.test_local_apply_gate import make_instance


class LocalApplyAuditTests(unittest.TestCase):
    def test_audit_log_redacts_operator_token(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)

        result = run_local_apply(
            target_instance=instance,
            apply=True,
            operator_token="local-dev-token",
            confirmation=APPLY_CONFIRMATION,
        )
        audit = result["audit_log"]
        audit_path = instance / "logs" / "local_apply" / f"{audit['audit_id']}.json"
        text = audit_path.read_text(encoding="utf-8")
        payload = json.loads(text)

        self.assertTrue(result["audit_log_created"])
        self.assertNotIn("local-dev-token", text)
        self.assertFalse(payload["operator_context_redacted"]["operator_token_stored"])
        self.assertFalse(payload["raw_token_stored"])


if __name__ == "__main__":
    unittest.main()
