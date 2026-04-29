from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_DIR = REPO_ROOT / "control" / "audits" / "windows-7-winforms-native-skeleton-planning-v0"
PLAN_JSON = PLAN_DIR / "winforms_skeleton_plan.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_windows_winforms_skeleton_plan.py"

REQUIRED_FILES = {
    "README.md",
    "SCOPE.md",
    "PROJECT_LAYOUT_DECISION.md",
    "NAMESPACE_DECISION.md",
    "BUILD_HOST_REQUIREMENTS.md",
    "ALLOWED_INITIAL_FEATURES.md",
    "PROHIBITED_INITIAL_FEATURES.md",
    "DATA_INPUTS.md",
    "UI_BOUNDARY.md",
    "TEST_PLAN.md",
    "APPROVAL_GATE.md",
    "RISKS.md",
    "NEXT_IMPLEMENTATION_PROMPT_REQUIREMENTS.md",
    "winforms_skeleton_plan.json",
}


class WindowsWinFormsSkeletonPlanningTestCase(unittest.TestCase):
    def test_planning_pack_exists(self) -> None:
        self.assertTrue(PLAN_DIR.is_dir())
        present = {path.name for path in PLAN_DIR.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_FILES.issubset(present))

    def test_plan_json_records_path_namespace_and_scope(self) -> None:
        payload = _load_json(PLAN_JSON)

        self.assertEqual(payload["status"], "planning_only")
        self.assertFalse(payload["implementation_started"])
        self.assertEqual(payload["lane"]["lane_id"], "windows_7_x64_winforms_net48")
        self.assertEqual(payload["proposed_project_path"], "clients/windows/winforms-net48/")
        self.assertEqual(payload["proposed_namespace"], "Eureka.Clients.Windows.WinForms")
        self.assertFalse(payload["project_path_created"])
        self.assertFalse(payload["visual_studio_solution_created"])
        self.assertFalse(payload["csproj_created"])
        self.assertFalse(payload["csharp_source_created"])

        scope = payload["initial_scope"]
        self.assertTrue(scope["read_only"])
        self.assertTrue(scope["demo_only"])
        self.assertTrue(scope["no_network_by_default"])
        self.assertFalse(scope["downloads_enabled"])
        self.assertFalse(scope["installers_enabled"])
        self.assertFalse(scope["cache_runtime_enabled"])
        self.assertFalse(scope["telemetry_enabled"])
        self.assertFalse(scope["rust_ffi_enabled"])

    def test_build_host_requirements_are_present(self) -> None:
        payload = _load_json(PLAN_JSON)
        requirements = set(payload["build_host_requirements"])

        self.assertTrue(
            {
                "Windows host",
                "Visual Studio 2022",
                ".NET Framework 4.8 targeting pack or developer pack",
                "WinForms desktop workload support",
                "x64 build target",
                "Windows 7 SP1+ x64 runtime compatibility verification",
            }.issubset(requirements)
        )

    def test_prohibited_features_are_present(self) -> None:
        payload = _load_json(PLAN_JSON)
        prohibited = set(payload["prohibited_initial_features"])

        self.assertTrue(
            {
                "downloads",
                "installers",
                "local cache runtime",
                "private file ingestion",
                "telemetry",
                "accounts",
                "live backend dependency",
                "live source probes",
                "Rust FFI",
                "relay runtime",
                "production readiness claims",
            }.issubset(prohibited)
        )

    def test_docs_state_approval_required_and_no_implementation(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in PLAN_DIR.glob("*.md"))

        self.assertIn("Human approval is required before any implementation", text)
        self.assertIn("No directory is created by this milestone", text)
        self.assertIn("No C# namespace or source file is created", text)
        self.assertIn("read-only and demo-only", text)
        self.assertIn("does not create a Visual Studio solution", text)

    def test_no_native_project_files_were_added(self) -> None:
        forbidden_suffixes = {
            ".sln",
            ".csproj",
            ".cs",
            ".resx",
            ".vcxproj",
            ".xcodeproj",
            ".xcworkspace",
            ".pbxproj",
        }
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.rglob("*")
            if ".git" not in path.parts
            and "__pycache__" not in path.parts
            and path.suffix.casefold() in forbidden_suffixes
        ]

        self.assertEqual(offenders, [])

    def test_validator_passes_and_json_parses(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn("status: valid", plain.stdout)

        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

