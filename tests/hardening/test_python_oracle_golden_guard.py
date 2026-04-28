import json
import unittest

from tests.hardening.helpers import find_private_path_leaks, load_json, repo_path, run_python


REQUIRED_GOLDEN_FAMILIES = {
    "source_registry": [
        "sources_list.json",
        "source_synthetic_fixtures.json",
        "source_github_releases_recorded_fixtures.json",
        "source_internet_archive_recorded_fixtures.json",
        "source_local_bundle_fixtures.json",
        "source_article_scan_recorded_fixtures.json",
    ],
    "query_planner": [
        "windows_7_apps.json",
        "windows_nt_61_utilities.json",
        "windows_xp_software.json",
        "windows_98_registry_repair.json",
        "latest_firefox_before_xp_support_ended.json",
        "latest_vlc_for_windows_xp.json",
        "old_blue_ftp_client_xp.json",
        "driver_thinkpad_t42_wifi_windows_2000.json",
        "creative_ct1740_driver_windows_98.json",
        "driver_inside_support_cd.json",
        "installer_inside_iso.json",
        "manual_sound_blaster_ct1740.json",
        "mac_os_9_browser.json",
        "powerpc_mac_os_x_10_4_browser.json",
        "article_ray_tracing_1994_magazine.json",
        "generic_unknown_query.json",
    ],
    "resolution_runs": [
        "exact_resolution_known.json",
        "exact_resolution_missing.json",
        "deterministic_search_archive.json",
        "planned_search_latest_firefox_xp.json",
    ],
    "local_index": [
        "status_after_build.json",
        "query_synthetic.json",
        "query_archive.json",
        "query_no_result.json",
    ],
    "resolution_memory": [
        "memory_from_exact_resolution.json",
        "memory_from_planned_search.json",
        "memory_from_absence.json",
    ],
    "archive_resolution_evals": [
        "suite_summary.json",
        "full_report.json",
    ],
}


class PythonOracleGoldenGuardTest(unittest.TestCase):
    def test_python_oracle_golden_check_passes(self):
        completed = run_python(["scripts/generate_python_oracle_golden.py", "--check"], timeout=120)
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)

    def test_manifest_and_required_families_exist(self):
        manifest = load_json("tests/parity/golden/python_oracle/v0/manifest.json")
        self.assertIn("authoritative", manifest["python_oracle_status"])
        self.assertIn("source_registry", manifest["included_seams"])

        root = repo_path("tests/parity/golden/python_oracle/v0")
        for family, filenames in REQUIRED_GOLDEN_FAMILIES.items():
            family_dir = root / family
            self.assertTrue(family_dir.exists(), family)
            for filename in filenames:
                path = family_dir / filename
                self.assertTrue(path.exists(), str(path))
                json.loads(path.read_text(encoding="utf-8"))

    def test_committed_goldens_do_not_leak_private_paths(self):
        root = repo_path("tests/parity/golden/python_oracle/v0")
        leaks = []
        for path in sorted(root.rglob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for leak in find_private_path_leaks(payload):
                leaks.append(f"{path.relative_to(repo_path('.'))}: {leak}")
        self.assertEqual(leaks, [])


if __name__ == "__main__":
    unittest.main()
