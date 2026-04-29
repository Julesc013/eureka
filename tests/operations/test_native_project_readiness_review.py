from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW_DIR = REPO_ROOT / "control" / "audits" / "native-client-project-readiness-v0"
REPORT = REVIEW_DIR / "native_readiness_report.json"
LANES = REPO_ROOT / "control" / "inventory" / "publication" / "native_client_lanes.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_native_project_readiness_review.py"

REQUIRED_FILES = {
    "README.md",
    "CURRENT_STATE.md",
    "CONTRACT_COVERAGE.md",
    "LANE_READINESS.md",
    "RISK_REGISTER.md",
    "READINESS_DECISION.md",
    "PRE_NATIVE_CHECKLIST.md",
    "NEXT_STEPS.md",
    "native_readiness_report.json",
}


class NativeProjectReadinessReviewTestCase(unittest.TestCase):
    def test_review_pack_exists(self) -> None:
        self.assertTrue(REVIEW_DIR.is_dir())
        present = {path.name for path in REVIEW_DIR.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_FILES.issubset(present))

    def test_report_decision_and_lane_are_valid(self) -> None:
        report = _load_json(REPORT)
        lanes = _load_json(LANES)
        lane_ids = {lane["lane_id"] for lane in lanes["lanes"]}

        self.assertEqual(report["report_id"], "native_client_project_readiness_review_v0")
        self.assertEqual(
            report["decision"],
            "ready_for_minimal_project_skeleton_after_human_approval",
        )
        self.assertIn(report["first_candidate_lane"], lane_ids)
        self.assertEqual(report["first_candidate_lane"], "windows_7_x64_winforms_net48")
        self.assertTrue(report["human_approval_required"])
        self.assertFalse(report["native_gui_implemented"])
        self.assertFalse(report["native_project_files_added"])
        self.assertFalse(report["production_ready"])

    def test_report_includes_blockers_and_prohibited_scope(self) -> None:
        report = _load_json(REPORT)
        blockers = " ".join(report["blockers"]).casefold()
        prohibited = set(report["prohibited_initial_scope"])

        self.assertIn("explicit human approval", blockers)
        self.assertIn("build host", blockers)
        self.assertTrue(
            {
                "downloads",
                "installers",
                "local cache runtime",
                "private file ingestion",
                "telemetry",
                "accounts",
                "cloud sync",
                "relay runtime",
                "live probes",
                "Rust FFI",
                "production readiness claims",
            }.issubset(prohibited)
        )

    def test_pre_native_checklist_is_unsigned_future_and_gated(self) -> None:
        checklist = (REVIEW_DIR / "PRE_NATIVE_CHECKLIST.md").read_text(encoding="utf-8")

        self.assertIn("Status: unsigned and future", checklist)
        self.assertIn("Human explicitly approves native project scaffolding", checklist)
        self.assertIn("No installer automation is approved", checklist)
        self.assertIn("No telemetry, analytics, accounts, cloud sync", checklist)
        self.assertIn("Operator signoff is recorded", checklist)

    def test_readiness_docs_do_not_claim_native_app_implemented(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8") for path in REVIEW_DIR.glob("*.md")
        ).casefold()

        self.assertIn("no gui native app is implemented", text)
        self.assertIn("must not create visual studio project files", text)
        self.assertNotIn("native apps are implemented", text)
        self.assertNotIn("production-ready native", text)
        self.assertIn("manual observation batch 0 execution", text)

    def test_no_native_project_files_exist(self) -> None:
        forbidden_suffixes = {
            ".sln",
            ".vcxproj",
            ".csproj",
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
