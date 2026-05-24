from __future__ import annotations

from pathlib import Path
import unittest

from runtime.local.apply import APPLY_CONFIRMATION, ROLLBACK_CONFIRMATION, run_local_apply, run_rollback
from tests.runtime.test_local_apply_gate import make_instance


class LocalApplyRollbackTests(unittest.TestCase):
    def test_rollback_restores_backup_hashes(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)
        apply_result = run_local_apply(
            target_instance=instance,
            apply=True,
            operator_token="local-dev-token",
            confirmation=APPLY_CONFIRMATION,
        )
        rollback_plan = apply_result["rollback_plan"]

        result = run_rollback(
            rollback_plan,
            operator_context={
                "apply": True,
                "operator_token": "local-dev-token",
                "confirmation": ROLLBACK_CONFIRMATION,
            },
        )

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["post_rollback_validation_passed"])
        self.assertTrue(Path(instance / "logs" / "local_apply" / f"{rollback_plan['rollback_plan_id']}.rollback.json").exists())


if __name__ == "__main__":
    unittest.main()
