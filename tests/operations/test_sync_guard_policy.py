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
            "control/inventory/git/branch_role_policy.json",
            "control/inventory/git/sync_workflow_commands.json",
            "docs/operations/MULTI_MACHINE_GIT_WORKFLOW.md",
            "docs/operations/AIDE_SYNC_GUARD.md",
            "docs/operations/AIDE_SYNC_RECOVERY_COMMANDS.md",
            ".aide/prompts/AIDE-SYNC-01.md",
            ".aide/prompts/AIDE-MERGE-01.md",
            ".aide/prompts/AIDE-RESCUE-01.md",
            "scripts/aide_merge_task_branch_to_main.py",
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

    def test_branch_role_policy_defines_canonical_and_temporary_branches(self):
        policy = self.load_json("control/inventory/git/branch_role_policy.json")
        self.assertEqual(policy["current_canonical_branch"], "main")
        durable_roles = {entry["role"] for entry in policy["durable_branch_roles"]}
        temporary_roles = {entry["role"] for entry in policy["temporary_branch_roles"]}
        self.assertIn("canonical", durable_roles)
        self.assertIn("development_channel_future", durable_roles)
        self.assertIn("release_channel_future", durable_roles)
        self.assertIn("local_task_branch", temporary_roles)
        self.assertIn("shared_task_branch", temporary_roles)
        self.assertIs(policy["safe_pruning_rules"]["force_delete_allowed"], False)
        self.assertIn("new_durable_channel", policy["branch_policy_extension_points"])
        self.assertEqual(policy["promotion_target_policy"]["helper_flag"], "--target-branch <branch>")

    def test_aide_merge_workflow_pushes_main_and_optionally_publishes_branch(self):
        workflow = self.load_json("control/inventory/git/sync_workflow_commands.json")
        merge = next(command for command in workflow["commands"] if command["command_id"] == "AIDE-MERGE-01")
        allowed = "\n".join(merge["allowed_commands"])
        self.assertIn("python scripts/aide_merge_task_branch_to_main.py", allowed)
        self.assertIn("git merge --no-ff <task-branch>", allowed)
        self.assertIn("git push -u origin <task-branch>", allowed)
        self.assertIn("git push origin main", allowed)
        self.assertIn("git branch -d <task-branch>", allowed)


if __name__ == "__main__":
    unittest.main()
