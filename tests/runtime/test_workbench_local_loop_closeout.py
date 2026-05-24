from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.local_loop import APPLY_CONFIRMATION, build_local_loop_plan, run_local_loop_dry_run, run_local_loop_temp_instance
from scripts.eureka_init_instance import initialize_instance


def make_instance() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix="eureka-local-loop-test-")
    instance = Path(tmp.name) / "instance"
    result = initialize_instance(instance)
    if result["status"] not in {"pass", "pass_with_warnings"}:
        tmp.cleanup()
        raise AssertionError(result)
    return tmp, instance


class WorkbenchLocalLoopCloseoutTests(unittest.TestCase):
    def test_dry_run_loop_does_not_mutate(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)
        before = (instance / "db" / "public_index.sqlite").read_bytes()
        plan = build_local_loop_plan("sampleproject", instance)

        result = run_local_loop_dry_run(plan)

        self.assertEqual(result["status"], "dry_run")
        self.assertTrue(result["dry_run_loop_passed"])
        self.assertFalse(result["operator_instance_mutated"])
        self.assertEqual(before, (instance / "db" / "public_index.sqlite").read_bytes())

    def test_temp_apply_loop_passes(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)
        plan = build_local_loop_plan("sampleproject", instance)

        result = run_local_loop_temp_instance(
            plan,
            {
                "use_temp_instance": True,
                "apply_to_temp": True,
                "operator_token": "local-dev-token",
                "confirmation": APPLY_CONFIRMATION,
                "projection_profile": "operator_workbench",
            },
        )

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["temp_apply_loop_passed"])
        self.assertTrue(result["search_after_apply_passed"])
        self.assertTrue(result["rollback_passed"])
        self.assertTrue(result["search_after_rollback_passed"])
        self.assertFalse(result["operator_instance_mutated"])
        self.assertFalse(result["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
