import json
import unittest
from pathlib import Path

from scripts.validate_native_skeleton import PROJECT_ALLOWLIST, validate_native_skeleton

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeSkeletonTests(unittest.TestCase):
    def test_native_skeleton_validates(self) -> None:
        report = validate_native_skeleton(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report)

    def test_required_native_directories_exist(self) -> None:
        policy = json.loads((REPO_ROOT / "control" / "inventory" / "native" / "native_directory_policy.json").read_text(encoding="utf-8"))
        for relative in policy["required_directories"]:
            self.assertTrue((REPO_ROOT / relative).is_dir(), relative)

    def test_forbidden_directory_names_are_absent(self) -> None:
        policy = json.loads((REPO_ROOT / "control" / "inventory" / "native" / "native_directory_policy.json").read_text(encoding="utf-8"))
        forbidden = set(policy["forbidden_directory_names"])
        offenders = [
            path.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "native").rglob("*")
            if path.is_dir() and path.name in forbidden
        ]
        self.assertEqual(offenders, [])

    def test_winforms_project_files_exist(self) -> None:
        for relative in PROJECT_ALLOWLIST:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_winforms_proof_is_read_only_by_policy(self) -> None:
        policy = json.loads((REPO_ROOT / "control" / "inventory" / "native" / "native_readonly_client_policy.json").read_text(encoding="utf-8"))
        self.assertIs(policy["read_only"], True)
        self.assertIs(policy["snapshot_input_allowed"], True)
        self.assertIs(policy["relay_fixture_input_allowed"], True)
        for key in (
            "live_source_access_allowed",
            "download_allowed",
            "install_allowed",
            "execute_allowed",
            "upload_allowed",
            "account_auth_allowed",
            "telemetry_allowed",
            "public_index_mutation_allowed",
            "master_index_mutation_allowed",
        ):
            self.assertIs(policy[key], False, key)

    def test_no_build_output_binaries_are_committed(self) -> None:
        suffixes = {".exe", ".dll", ".pdb", ".obj", ".o", ".a", ".lib", ".msi"}
        offenders = [
            path.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "native").rglob("*")
            if path.is_file() and path.suffix.casefold() in suffixes
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
