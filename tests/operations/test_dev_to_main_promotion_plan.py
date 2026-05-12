from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "prepare_dev_to_main_promotion.py"


def load_module():
    spec = importlib.util.spec_from_file_location("prepare_dev_to_main_promotion", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def make_git_fixture(root: Path, *, review_ready: bool = False) -> None:
    run(["git", "init", "-b", "main"], root)
    run(["git", "config", "user.email", "r0-test@example.invalid"], root)
    run(["git", "config", "user.name", "R0 Test"], root)
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    run(["git", "add", "README.md"], root)
    run(["git", "commit", "-m", "initial"], root)
    run(["git", "checkout", "-b", "dev"], root)
    (root / "control/inventory").mkdir(parents=True, exist_ok=True)
    (root / "control/inventory/r0_production_review_result.json").write_text(
        json.dumps({"dev_can_promote_to_main": review_ready}) + "\n",
        encoding="utf-8",
    )
    run(["git", "add", "control/inventory/r0_production_review_result.json"], root)
    run(["git", "commit", "-m", "review"], root)


class DevToMainPromotionPlanTests(unittest.TestCase):
    def test_promotion_plan_does_not_merge_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo, review_ready=True)
            module = load_module()
            plan = module.build_promotion_plan(repo)
            self.assertTrue(plan["promotion_plan_only"])
            self.assertFalse(plan["branch_mutation_performed"])
            self.assertTrue(plan["ready"])

    def test_promotion_plan_records_branch_mutation_false_by_default(self):
        module = load_module()
        plan = module.build_promotion_plan(ROOT)
        self.assertTrue(plan["promotion_plan_only"])
        self.assertFalse(plan["branch_mutation_performed"])

    def test_apply_is_blocked_without_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo, review_ready=True)
            output = repo / "control/inventory/dev_to_main_promotion_plan.json"
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--apply", "--output", str(output), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, proc.returncode)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(payload["branch_mutation_performed"])
            self.assertFalse(payload["ready"])

    def test_refuses_forbidden_output_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_git_fixture(repo, review_ready=True)
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--output", str(repo / "runtime/out.json")],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing forbidden output root", proc.stderr + proc.stdout)

    def test_no_network_or_provider_imports(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            self.assertFalse({"requests", "urllib", "httpx", "aiohttp", "openai", "anthropic"} & set(names))


if __name__ == "__main__":
    unittest.main()
