from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from tests.operations.test_r0_final_promotion import make_git_fixture


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "prepare_r0_dev_to_main_merge.py"


def load_module():
    spec = importlib.util.spec_from_file_location("prepare_r0_dev_to_main_merge", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class R0DevToMainMergePlanTests(unittest.TestCase):
    def test_merge_plan_defaults_to_no_branch_mutation(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo)
            plan = module.build_merge_plan(repo)
            self.assertTrue(plan["promotion_plan_only"])
            self.assertFalse(plan["branch_mutation_performed"])
            self.assertFalse(plan["merge_performed"])
            self.assertFalse(plan["push_main_performed"])

    def test_merge_plan_refuses_force_push(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo)
            plan = module.build_merge_plan(repo)
            joined_steps = "\n".join(plan["promotion_steps"] + plan["forbidden_operations"])
            self.assertIn("git push --force", joined_steps)
            self.assertFalse(any("--force" in step for step in plan["promotion_steps"]))

    def test_merge_plan_records_rollback_steps(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo)
            plan = module.build_merge_plan(repo)
            rollback = "\n".join(plan["rollback_plan"]).lower()
            self.assertIn("revert", rollback)
            self.assertIn("never rewrite main history", rollback)


if __name__ == "__main__":
    unittest.main()
