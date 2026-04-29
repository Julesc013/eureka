from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
CONTRACT = PUBLICATION_DIR / "native_client_contract.json"
LANES = PUBLICATION_DIR / "native_client_lanes.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_native_client_contract.py"
DOCS = [
    REPO_ROOT / "docs" / "reference" / "NATIVE_CLIENT_CONTRACT.md",
    REPO_ROOT / "docs" / "reference" / "NATIVE_CLIENT_LANES.md",
    REPO_ROOT / "docs" / "operations" / "NATIVE_CLIENT_READINESS_CHECKLIST.md",
]


class NativeClientContractTestCase(unittest.TestCase):
    def test_contract_inventory_is_design_only(self) -> None:
        contract = _load_json(CONTRACT)

        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["status"], "design_only")
        self.assertFalse(contract["native_gui_implemented"])
        self.assertTrue(contract["cli_surface_implemented"])
        self.assertEqual(contract["first_candidate_lane"], "windows_7_x64_winforms_net48")
        self.assertEqual(contract["created_by_slice"], "native_client_contract_v0")

    def test_native_lanes_inventory_contains_required_lanes(self) -> None:
        lanes = _load_json(LANES)
        by_id = {lane["lane_id"]: lane for lane in lanes["lanes"]}

        self.assertEqual(
            set(by_id),
            {
                "windows_7_x64_winforms_net48",
                "windows_xp_x86_win32_unicode",
                "windows_95_nt4_x86_win32_ansi",
                "windows_win16_research",
                "windows_modern_winui_future",
                "macos_10_6_10_15_intel_appkit",
                "macos_11_plus_modern",
                "macos_10_4_10_5_ppc_intel_research",
                "classic_mac_7_1_9_2_research",
            },
        )
        for lane in by_id.values():
            with self.subTest(lane=lane["lane_id"]):
                self.assertIn(lane["status"], {"future", "future_deferred", "lab_verify", "research"})
                self.assertNotEqual(lane["status"], "implemented")
                self.assertIn("installer automation", json.dumps(lane).casefold())
                self.assertIn("private data by default", json.dumps(lane).casefold())

    def test_cli_flag_aligns_with_current_cli_surface(self) -> None:
        contract = _load_json(CONTRACT)

        self.assertTrue((REPO_ROOT / "surfaces" / "native" / "cli").is_dir())
        self.assertTrue(contract["cli_surface_implemented"])
        self.assertFalse(contract["native_gui_implemented"])

    def test_dependencies_and_prohibitions_are_represented(self) -> None:
        contract = _load_json(CONTRACT)
        text = json.dumps(contract).casefold()

        self.assertIn("snapshot_consumer_contract", text)
        self.assertIn("public_site/data/", text)
        self.assertIn("live_backend_dependency", text)
        self.assertIn("relay_dependency", text)
        self.assertIn("parity_only_unwired", text)
        self.assertIn("installer automation", text)
        self.assertIn("download executable artifacts", text)
        self.assertIn("native_ffi_implemented", text)
        self.assertFalse(contract["rust_dependency_status"]["production_rust_backend"])

    def test_docs_and_checklist_exist_and_state_limits(self) -> None:
        for path in DOCS:
            self.assertTrue(path.is_file(), path)
        text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS).casefold()

        for phrase in (
            "does not create a visual studio project",
            "does not create a native gui",
            "cli remains the only current local native-like surface",
            "status: future/unsigned",
            "no private data is consumed by default",
            "no rust ffi or runtime wiring is assumed",
        ):
            self.assertIn(phrase, text)

    def test_no_native_project_files_exist(self) -> None:
        forbidden_suffixes = {".sln", ".vcxproj", ".csproj", ".xcodeproj", ".xcworkspace", ".pbxproj"}
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.rglob("*")
            if ".git" not in path.parts and path.suffix.casefold() in forbidden_suffixes
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
        self.assertFalse(payload["native_gui_implemented"])
        self.assertTrue(payload["cli_surface_implemented"])


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
