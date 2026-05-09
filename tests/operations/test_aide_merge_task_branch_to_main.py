import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
MERGE_SCRIPT = REPO_ROOT / "scripts/aide_merge_task_branch_to_main.py"
GUARD_SCRIPT = REPO_ROOT / "scripts/check_git_task_state.py"


class AideMergeTaskBranchToMainTest(unittest.TestCase):
    def git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)

    def init_repo_with_remote(self, base: Path) -> tuple[Path, Path]:
        remote = base / "origin.git"
        repo = base / "repo"
        repo.mkdir()
        self.assertEqual(subprocess.run(["git", "init", "--bare", str(remote)], text=True, capture_output=True).returncode, 0)
        self.assertEqual(self.git(repo, "init", "-b", "main").returncode, 0)
        self.assertEqual(self.git(repo, "config", "user.name", "Eureka Test").returncode, 0)
        self.assertEqual(self.git(repo, "config", "user.email", "eureka-test@example.invalid").returncode, 0)
        (repo / "README.md").write_text("fixture\n", encoding="utf-8")
        self.assertEqual(self.git(repo, "add", "README.md").returncode, 0)
        self.assertEqual(self.git(repo, "commit", "-m", "init").returncode, 0)
        self.assertEqual(self.git(repo, "remote", "add", "origin", str(remote)).returncode, 0)
        self.assertEqual(self.git(repo, "push", "-u", "origin", "main").returncode, 0)
        return repo, remote

    def test_merge_helper_merges_local_branch_and_pushes_main(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, _remote = self.init_repo_with_remote(Path(temp_dir))
            self.assertEqual(self.git(repo, "switch", "-c", "task/sync-push-01").returncode, 0)
            (repo / "task.txt").write_text("task\n", encoding="utf-8")
            self.assertEqual(self.git(repo, "add", "task.txt").returncode, 0)
            self.assertEqual(self.git(repo, "commit", "-m", "task work").returncode, 0)

            result = subprocess.run(
                [
                    sys.executable,
                    str(MERGE_SCRIPT),
                    "--repo",
                    str(repo),
                    "--task-id",
                    "SYNC-PUSH-01",
                    "--branch",
                    "task/sync-push-01",
                    "--guard-script",
                    str(GUARD_SCRIPT),
                    "--execute",
                ],
                text=True,
                capture_output=True,
                timeout=120,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(self.git(repo, "branch", "--show-current").stdout.strip(), "main")
            self.assertEqual(self.git(repo, "rev-list", "--left-right", "--count", "main...origin/main").stdout.strip(), "0\t0")
            self.assertEqual((repo / "task.txt").read_text(encoding="utf-8"), "task\n")
            self.assertNotIn("origin/task/sync-push-01", self.git(repo, "branch", "-r").stdout)

    def test_merge_helper_can_publish_and_prune_shared_branch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, _remote = self.init_repo_with_remote(Path(temp_dir))
            self.assertEqual(self.git(repo, "switch", "-c", "task/shared-sync-01").returncode, 0)
            (repo / "shared.txt").write_text("shared\n", encoding="utf-8")
            self.assertEqual(self.git(repo, "add", "shared.txt").returncode, 0)
            self.assertEqual(self.git(repo, "commit", "-m", "shared work").returncode, 0)

            result = subprocess.run(
                [
                    sys.executable,
                    str(MERGE_SCRIPT),
                    "--repo",
                    str(repo),
                    "--task-id",
                    "SHARED-SYNC-01",
                    "--branch",
                    "task/shared-sync-01",
                    "--guard-script",
                    str(GUARD_SCRIPT),
                    "--execute",
                    "--publish-branch",
                    "--delete-merged-branch",
                    "--delete-remote-branch",
                ],
                text=True,
                capture_output=True,
                timeout=120,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(self.git(repo, "branch", "--show-current").stdout.strip(), "main")
            self.assertNotIn("task/shared-sync-01", self.git(repo, "branch").stdout)
            self.assertNotIn("origin/task/shared-sync-01", self.git(repo, "branch", "-r").stdout)

    def test_merge_helper_default_dry_run_does_not_switch_branches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, _remote = self.init_repo_with_remote(Path(temp_dir))
            self.assertEqual(self.git(repo, "switch", "-c", "task/sync-push-01").returncode, 0)

            result = subprocess.run(
                [
                    sys.executable,
                    str(MERGE_SCRIPT),
                    "--repo",
                    str(repo),
                    "--task-id",
                    "SYNC-PUSH-01",
                    "--branch",
                    "task/sync-push-01",
                    "--guard-script",
                    str(GUARD_SCRIPT),
                ],
                text=True,
                capture_output=True,
                timeout=120,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("dry_run", result.stdout)
            self.assertEqual(self.git(repo, "branch", "--show-current").stdout.strip(), "task/sync-push-01")
