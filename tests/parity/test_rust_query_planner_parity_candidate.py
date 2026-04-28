from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = REPO_ROOT / "tests" / "parity" / "rust_query_planner_cases.json"
GOLDEN_ROOT = REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0"
RUST_QUERY_PLANNER = REPO_ROOT / "crates" / "eureka-core" / "src" / "query_planner.rs"
RUST_LIB = REPO_ROOT / "crates" / "eureka-core" / "src" / "lib.rs"


class RustQueryPlannerParityCandidateTestCase(unittest.TestCase):
    def test_fixture_map_and_goldens_cover_required_old_platform_cases(self) -> None:
        fixture = _load_json(CASES_PATH)
        cases = {case["case_id"]: case for case in fixture["cases"]}
        required = {
            "windows_7_apps",
            "windows_nt_61_utilities",
            "windows_xp_software",
            "windows_98_registry_repair",
            "latest_firefox_before_xp_support_ended",
            "latest_vlc_for_windows_xp",
            "driver_thinkpad_t42_wifi_windows_2000",
            "creative_ct1740_driver_windows_98",
            "old_blue_ftp_client_xp",
            "driver_inside_support_cd",
            "installer_inside_iso",
            "manual_sound_blaster_ct1740",
            "mac_os_9_browser",
            "powerpc_mac_os_x_10_4_browser",
            "article_ray_tracing_1994_magazine",
            "generic_unknown_query",
        }

        self.assertTrue(required.issubset(cases))
        self.assertTrue(fixture["python_remains_oracle"])
        self.assertFalse(fixture["runtime_wiring_allowed"])
        for case_id, case in cases.items():
            with self.subTest(case_id=case_id):
                golden_path = GOLDEN_ROOT / "query_planner" / case["python_oracle_file"]
                self.assertTrue(golden_path.is_file(), golden_path)
                golden = _load_json(golden_path)
                self.assertEqual(
                    golden["body"]["query_plan"]["task_kind"],
                    case["required_task_kind"],
                )

    def test_rust_candidate_declares_model_rules_and_golden_comparison(self) -> None:
        rust = RUST_QUERY_PLANNER.read_text(encoding="utf-8")
        lib = RUST_LIB.read_text(encoding="utf-8")

        self.assertIn("pub struct ResolutionTask", rust)
        self.assertIn("pub fn plan_query", rust)
        self.assertIn("pub fn query_plan_response", rust)
        self.assertIn("query_planner_candidate_matches_python_oracle_goldens", rust)
        self.assertIn("Windows NT 6.1", rust)
        self.assertIn("latest_before_support_drop", rust)
        self.assertIn("find_member_in_container", rust)
        self.assertIn("pub mod query_planner;", lib)

    def test_rust_is_not_wired_into_python_runtime_or_surfaces(self) -> None:
        forbidden = re.compile(r"query_planner_parity_candidate|eureka_core|eureka-core")
        violations: list[str] = []
        for root in [REPO_ROOT / "runtime", REPO_ROOT / "surfaces"]:
            for path in root.rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                if forbidden.search(text):
                    violations.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(violations, [])

    def test_docs_keep_python_as_oracle_and_rust_isolated(self) -> None:
        docs = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in [
                REPO_ROOT / "tests" / "parity" / "README.md",
                REPO_ROOT / "tests" / "parity" / "PARITY_PLAN.md",
                REPO_ROOT / "docs" / "architecture" / "RUST_BACKEND_LANE.md",
                REPO_ROOT / "docs" / "roadmap" / "RUST_MIGRATION.md",
            ]
        )

        self.assertIn("rust query planner parity candidate v0", docs)
        self.assertIn("python remains", docs)
        self.assertIn("oracle", docs)
        self.assertIn("not wired", docs)
        self.assertNotIn("rust is the active backend", docs)
        self.assertNotIn("rust replaces python", docs)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
