from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.local_loop import APPLY_CONFIRMATION, build_local_loop_plan, run_local_loop_temp_instance
from scripts.eureka_init_instance import initialize_instance


class LocalLoopRollbackTests(unittest.TestCase):
    def test_rollback_restores_temp_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-local-loop-rollback-") as tmp:
            instance = Path(tmp) / "instance"
            initialize_instance(instance)
            result = run_local_loop_temp_instance(
                build_local_loop_plan("sampleproject", instance),
                {
                    "use_temp_instance": True,
                    "apply_to_temp": True,
                    "operator_token": "local-dev-token",
                    "confirmation": APPLY_CONFIRMATION,
                    "projection_profile": "operator_workbench",
                },
            )

            proof = result["search_after_apply_proof"]["search_after_rollback"]
            self.assertTrue(result["rollback_passed"])
            self.assertTrue(proof["search_after_rollback_passed"])
            self.assertEqual(proof["search_result_count_after_rollback"], 0)
            self.assertFalse(result["operator_instance_mutated"])


if __name__ == "__main__":
    unittest.main()
