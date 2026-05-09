import io
import tempfile
import tarfile
import unittest
from pathlib import Path

from runtime.extraction.guards import check_path_safety, load_extraction_policy
from runtime.extraction.sandbox import run_fixture_extraction, target_from_fixture
from runtime.extraction.tier1_member_listing import extract_tier1_member_listing


REPO_ROOT = Path(__file__).resolve().parents[2]


class ExtractionGuardsTest(unittest.TestCase):
    def setUp(self):
        self.policy = load_extraction_policy()

    def test_path_traversal_member_is_blocked(self):
        target = {
            **target_from_fixture("examples/extraction/fixtures/path_traversal_blocked/path_traversal_blocked.zip", ["0", "1"]),
            "target_id": "extraction.target.path_traversal_blocked.test.v0",
        }
        result = run_fixture_extraction(target, ["0", "1"], self.policy)
        self.assertEqual(result["extraction_status"], "blocked_path_traversal")
        self.assertTrue(result["blocked_members"])

    def test_absolute_drive_and_null_paths_are_blocked(self):
        self.assertFalse(check_path_safety("/tmp/file.txt", self.policy)["path_safe"])
        self.assertFalse(check_path_safety("C:/tmp/file.txt", self.policy)["path_safe"])
        self.assertFalse(check_path_safety("safe/\x00name.txt", self.policy)["path_safe"])

    def test_symlink_is_blocked_or_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            tar_path = Path(tmp) / "symlink.tar"
            with tarfile.open(tar_path, "w") as archive:
                info = tarfile.TarInfo("link")
                info.type = tarfile.SYMTYPE
                info.linkname = "target"
                archive.addfile(info)
            members = extract_tier1_member_listing(tar_path, self.policy)
            self.assertTrue(members[0]["blocked"])
            self.assertIn("symlink", members[0]["block_reason"])

    def test_archive_bomb_risk_fixture_is_blocked(self):
        result = run_fixture_extraction(
            target_from_fixture("examples/extraction/fixtures/archive_bomb_blocked/archive_bomb_blocked.zip", ["0", "1"]),
            ["0", "1"],
            self.policy,
        )
        self.assertEqual(result["extraction_status"], "blocked_archive_bomb_risk")

    def test_no_execution_occurs_for_tar_listing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tar_path = Path(tmp) / "exec_named.tar"
            payload = b"echo should-not-run\n"
            with tarfile.open(tar_path, "w") as archive:
                info = tarfile.TarInfo("run.sh")
                info.mode = 0o755
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            result = run_fixture_extraction(target_from_fixture(tar_path, ["0", "1"]), ["0", "1"], self.policy)
            self.assertFalse(result["product_boundary"]["enabled_execution"])
            self.assertFalse(result["safety_report"]["execution_prevented"] is False)


if __name__ == "__main__":
    unittest.main()
