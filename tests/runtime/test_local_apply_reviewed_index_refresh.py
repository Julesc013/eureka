from __future__ import annotations

import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.apply import APPLY_CONFIRMATION, ROLLBACK_CONFIRMATION, run_local_apply, run_rollback
from tests.runtime.test_local_apply_gate import make_instance


class LocalApplyReviewedIndexRefreshTests(unittest.TestCase):
    def test_reviewed_index_refresh_applies_and_rolls_back_on_temp_instance(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)
        result = run_local_apply(
            target_instance=instance,
            apply=True,
            operator_token="local-dev-token",
            confirmation=APPLY_CONFIRMATION,
        )

        self.assertEqual(result["status"], "pass")
        self.assertGreater(result["post_apply_validation"]["search_result_count"], 0)

        rollback = run_rollback(
            result["rollback_plan"],
            operator_context={
                "apply": True,
                "operator_token": "local-dev-token",
                "confirmation": ROLLBACK_CONFIRMATION,
            },
        )
        self.assertEqual(rollback["status"], "pass")
        runtime = open_local_appliance(instance, read_only=True)
        try:
            self.assertEqual(len(runtime.public_index.search("sampleproject", limit=10)), 0)
        finally:
            close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
