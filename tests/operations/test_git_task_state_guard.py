import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD_SCRIPT = REPO_ROOT / "scripts" / "check_git_task_state.py"


class GitTaskStateGuardTest(unittest.TestCase):
    def run_guard(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GUARD_SCRIPT), *args],
            cwd=repo,
            text=True,
            capture_output=True,
        )

    def git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)

    def init_repo(self, repo: Path) -> None:
        self.assertEqual(self.git(repo, "init", "-b", "main").returncode, 0)
        self.assertEqual(self.git(repo, "config", "user.name", "Eureka Test").returncode, 0)
        self.assertEqual(self.git(repo, "config", "user.email", "eureka-test@example.invalid").returncode, 0)
        (repo / "README.md").write_text("fixture\n", encoding="utf-8")
        self.assertEqual(self.git(repo, "add", "README.md").returncode, 0)
        self.assertEqual(self.git(repo, "commit", "-m", "init").returncode, 0)

    def checkout_task_branch(self, repo: Path, name: str = "task/sync-guard-01") -> None:
        self.assertEqual(self.git(repo, "switch", "-c", name).returncode, 0)

    def attach_remote_and_push(self, repo: Path, remote: Path, branch: str = "main") -> None:
        self.assertEqual(self.git(repo, "remote", "add", "origin", str(remote)).returncode, 0)
        self.assertEqual(self.git(repo, "push", "-u", "origin", branch).returncode, 0)

    def test_clean_task_branch_passes_with_upstream(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            remote = base / "origin.git"
            repo = base / "repo"
            repo.mkdir()
            self.assertEqual(subprocess.run(["git", "init", "--bare", str(remote)], text=True, capture_output=True).returncode, 0)
            self.init_repo(repo)
            self.attach_remote_and_push(repo, remote)
            self.checkout_task_branch(repo)
            self.assertEqual(self.git(repo, "push", "-u", "origin", "task/sync-guard-01").returncode, 0)

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")

    def test_dirty_worktree_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self.init_repo(repo)
            self.checkout_task_branch(repo)
            (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "FAIL")

    def test_active_merge_marker_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self.init_repo(repo)
            self.checkout_task_branch(repo)
            head = self.git(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / ".git" / "MERGE_HEAD").write_text(head + "\n", encoding="utf-8")

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        payload = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no_merge_state", {check["check"] for check in payload["checks"] if check["status"] == "FAIL"})

    def test_active_rebase_marker_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self.init_repo(repo)
            self.checkout_task_branch(repo)
            (repo / ".git" / "rebase-merge").mkdir()

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        payload = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no_rebase_state", {check["check"] for check in payload["checks"] if check["status"] == "FAIL"})

    def test_active_cherry_pick_marker_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self.init_repo(repo)
            self.checkout_task_branch(repo)
            head = self.git(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / ".git" / "CHERRY_PICK_HEAD").write_text(head + "\n", encoding="utf-8")

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        payload = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no_cherry_pick_state", {check["check"] for check in payload["checks"] if check["status"] == "FAIL"})

    def test_main_fails_unless_allow_main(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self.init_repo(repo)

            denied = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")
            allowed = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--allow-main", "--json")

        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(json.loads(denied.stdout)["status"], "FAIL")
        self.assertEqual(allowed.returncode, 0)
        self.assertEqual(json.loads(allowed.stdout)["status"], "WARN")

    def test_no_upstream_warns_without_failing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self.init_repo(repo)
            self.checkout_task_branch(repo)

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "WARN")
        self.assertIn("task_branch_upstream_status", {check["check"] for check in payload["checks"] if check["status"] == "WARN"})

    def test_branch_behind_upstream_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            remote = base / "origin.git"
            repo = base / "repo"
            peer = base / "peer"
            repo.mkdir()
            self.assertEqual(subprocess.run(["git", "init", "--bare", str(remote)], text=True, capture_output=True).returncode, 0)
            self.init_repo(repo)
            self.attach_remote_and_push(repo, remote)
            self.checkout_task_branch(repo)
            self.assertEqual(self.git(repo, "push", "-u", "origin", "task/sync-guard-01").returncode, 0)

            self.assertEqual(subprocess.run(["git", "clone", str(remote), str(peer)], text=True, capture_output=True).returncode, 0)
            self.assertEqual(self.git(peer, "config", "user.name", "Eureka Test").returncode, 0)
            self.assertEqual(self.git(peer, "config", "user.email", "eureka-test@example.invalid").returncode, 0)
            self.assertEqual(self.git(peer, "switch", "task/sync-guard-01").returncode, 0)
            (peer / "remote.txt").write_text("remote\n", encoding="utf-8")
            self.assertEqual(self.git(peer, "add", "remote.txt").returncode, 0)
            self.assertEqual(self.git(peer, "commit", "-m", "remote task update").returncode, 0)
            self.assertEqual(self.git(peer, "push").returncode, 0)
            self.assertEqual(self.git(repo, "fetch", "origin").returncode, 0)

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        payload = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("task_branch_not_behind_upstream", {check["check"] for check in payload["checks"] if check["status"] == "FAIL"})

    def test_secret_like_untracked_path_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            self.init_repo(repo)
            self.checkout_task_branch(repo)
            (repo / ".env").write_text("TOKEN=example\n", encoding="utf-8")

            result = self.run_guard(repo, "--mode", "start-task", "--task-id", "SYNC-GUARD-01", "--json")

        payload = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        failed_checks = {check["check"] for check in payload["checks"] if check["status"] == "FAIL"}
        self.assertIn("no_forbidden_private_paths", failed_checks)
        self.assertIn("no_untracked_secret_like_paths", failed_checks)

    def test_merge_task_fails_when_main_has_unpushed_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            remote = base / "origin.git"
            repo = base / "repo"
            repo.mkdir()
            self.assertEqual(subprocess.run(["git", "init", "--bare", str(remote)], text=True, capture_output=True).returncode, 0)
            self.init_repo(repo)
            self.attach_remote_and_push(repo, remote)
            (repo / "main-only.txt").write_text("local main\n", encoding="utf-8")
            self.assertEqual(self.git(repo, "add", "main-only.txt").returncode, 0)
            self.assertEqual(self.git(repo, "commit", "-m", "local main work").returncode, 0)

            result = self.run_guard(repo, "--mode", "merge-task", "--task-id", "SYNC-GUARD-01", "--allow-main", "--json")

        payload = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "FAIL")
        self.assertIn("no_unpushed_main_work", {check["check"] for check in payload["checks"] if check["status"] == "FAIL"})


if __name__ == "__main__":
    unittest.main()
