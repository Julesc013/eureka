import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class SyncGuardPolicyTest(unittest.TestCase):
    def load_json(self, relative: str):
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_policy_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_sync_guard_policy.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_required_policies_docs_and_prompts_exist(self):
        for relative in [
            "control/inventory/git/sync_guard_policy.json",
            "control/inventory/git/task_branch_policy.json",
            "control/inventory/git/sync_workflow_commands.json",
            "docs/operations/MULTI_MACHINE_GIT_WORKFLOW.md",
            "docs/operations/AIDE_SYNC_GUARD.md",
            "docs/operations/AIDE_SYNC_RECOVERY_COMMANDS.md",
            ".aide/prompts/AIDE-SYNC-01.md",
            ".aide/prompts/AIDE-MERGE-01.md",
            ".aide/prompts/AIDE-RESCUE-01.md",
        ]:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_forbidden_destructive_commands_are_listed(self):
        policy = self.load_json("control/inventory/git/sync_guard_policy.json")
        forbidden = set(policy["forbidden_operations"])
        for command in [
            "git push --force",
            "git reset --hard",
            "git clean -fd",
            "git stash pop",
            "git branch -D",
            "git rebase shared branches",
        ]:
            self.assertIn(command, forbidden)

    def test_product_boundary_remains_false(self):
        policy = self.load_json("control/inventory/git/sync_guard_policy.json")
        for field, value in policy["product_boundary"].items():
            self.assertIs(value, False, field)

    def test_workflow_commands_include_three_prompt_categories(self):
        workflow = self.load_json("control/inventory/git/sync_workflow_commands.json")
        command_ids = {command["command_id"] for command in workflow["commands"]}
        self.assertEqual(command_ids, {"AIDE-SYNC-01", "AIDE-MERGE-01", "AIDE-RESCUE-01"})


if __name__ == "__main__":
    unittest.main()
