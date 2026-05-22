from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_service.workbench_review_promote import run_review_promote_flow
from scripts.eureka_init_instance import initialize_instance


class ReviewedIndexRefreshFlowTests(unittest.TestCase):
    def test_temp_reviewed_index_refresh_works(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-review-promote-test-") as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertIn(initialize_instance(instance)["status"], {"pass", "pass_with_warnings"})
            runtime = open_local_appliance(instance)
            try:
                result = run_review_promote_flow(
                    operator_token="local-dev-token",
                    dry_run=False,
                    runtime=runtime,
                    apply_to_temp=True,
                )
            finally:
                close_local_appliance(runtime)
        self.assertTrue(result["temp_reviewed_index_refresh_passed"], result)
        self.assertTrue(result["temp_search_after_refresh_passed"], result)
        self.assertFalse(result["operator_instance_mutated"])
        self.assertFalse(result["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
