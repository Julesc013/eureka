from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_ROOT = REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0"
GENERATOR = REPO_ROOT / "scripts" / "generate_python_oracle_golden.py"

REQUIRED_FILES = (
    "manifest.json",
    "source_registry/sources_list.json",
    "source_registry/source_synthetic_fixtures.json",
    "source_registry/source_github_releases_recorded_fixtures.json",
    "source_registry/source_internet_archive_recorded_fixtures.json",
    "source_registry/source_local_bundle_fixtures.json",
    "source_registry/source_article_scan_recorded_fixtures.json",
    "query_planner/windows_7_apps.json",
    "query_planner/windows_nt_61_utilities.json",
    "query_planner/windows_xp_software.json",
    "query_planner/windows_98_registry_repair.json",
    "query_planner/latest_firefox_before_xp_support_ended.json",
    "query_planner/latest_vlc_for_windows_xp.json",
    "query_planner/old_blue_ftp_client_xp.json",
    "query_planner/driver_thinkpad_t42_wifi_windows_2000.json",
    "query_planner/creative_ct1740_driver_windows_98.json",
    "query_planner/driver_inside_support_cd.json",
    "query_planner/installer_inside_iso.json",
    "query_planner/manual_sound_blaster_ct1740.json",
    "query_planner/mac_os_9_browser.json",
    "query_planner/powerpc_mac_os_x_10_4_browser.json",
    "query_planner/article_ray_tracing_1994_magazine.json",
    "query_planner/generic_unknown_query.json",
    "resolution_runs/exact_resolution_known.json",
    "resolution_runs/exact_resolution_missing.json",
    "resolution_runs/deterministic_search_archive.json",
    "resolution_runs/planned_search_latest_firefox_xp.json",
    "local_index/status_after_build.json",
    "local_index/query_synthetic.json",
    "local_index/query_archive.json",
    "local_index/query_no_result.json",
    "resolution_memory/memory_from_exact_resolution.json",
    "resolution_memory/memory_from_planned_search.json",
    "resolution_memory/memory_from_absence.json",
    "archive_resolution_evals/suite_summary.json",
    "archive_resolution_evals/full_report.json",
)

REQUIRED_DIRECTORIES = (
    "source_registry",
    "query_planner",
    "resolution_runs",
    "local_index",
    "resolution_memory",
    "archive_resolution_evals",
)

EXPECTED_TASK_KINDS = {
    "windows_7_apps.json": "browse_software",
    "windows_nt_61_utilities.json": "browse_software",
    "windows_xp_software.json": "browse_software",
    "windows_98_registry_repair.json": "identify_software",
    "latest_firefox_before_xp_support_ended.json": "find_latest_compatible_release",
    "latest_vlc_for_windows_xp.json": "find_latest_compatible_release",
    "old_blue_ftp_client_xp.json": "identify_software",
    "driver_thinkpad_t42_wifi_windows_2000.json": "find_driver",
    "creative_ct1740_driver_windows_98.json": "find_driver",
    "driver_inside_support_cd.json": "find_member_in_container",
    "installer_inside_iso.json": "find_member_in_container",
    "manual_sound_blaster_ct1740.json": "find_documentation",
    "mac_os_9_browser.json": "browse_software",
    "powerpc_mac_os_x_10_4_browser.json": "browse_software",
    "article_ray_tracing_1994_magazine.json": "find_document_article",
    "generic_unknown_query.json": "generic_search",
}


class PythonOracleGoldenTestCase(unittest.TestCase):
    def test_manifest_exists_and_parses(self) -> None:
        manifest = _load_json("manifest.json")

        self.assertEqual(manifest["fixture_pack_id"], "python_oracle_golden_v0")
        self.assertEqual(manifest["created_by_slice"], "rust_parity_fixture_pack_v0")
        self.assertEqual(manifest["python_oracle_status"], "authoritative_reference_lane")
        self.assertIn("source_registry", manifest["included_seams"])
        self.assertIn("query_planner", manifest["included_seams"])
        self.assertIn("archive_resolution_evals", manifest["included_seams"])
        self.assertEqual(
            manifest["normalization_policy"]["local_index_fts_mode"],
            "<PYTHON_ORACLE_FTS_MODE_NORMALIZED>",
        )

    def test_required_directories_and_json_files_exist(self) -> None:
        self.assertTrue((GOLDEN_ROOT.parent.parent / "README.md").is_file())
        self.assertTrue((GOLDEN_ROOT.parent / "README.md").is_file())
        self.assertTrue((GOLDEN_ROOT / "README.md").is_file())
        for directory in REQUIRED_DIRECTORIES:
            self.assertTrue((GOLDEN_ROOT / directory).is_dir(), directory)
        for relative_path in REQUIRED_FILES:
            path = GOLDEN_ROOT / relative_path
            self.assertTrue(path.is_file(), relative_path)
            json.loads(path.read_text(encoding="utf-8"))

    def test_no_golden_json_contains_private_temp_paths(self) -> None:
        windows_absolute = re.compile(r"^[A-Za-z]:[\\/]")
        unix_temp = re.compile(r"^/(tmp|var/folders)/")
        temp_segment = re.compile(r"(^|[\\/])Temp([\\/]|$)")
        for path in GOLDEN_ROOT.rglob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for value in _iter_string_values(payload):
                self.assertIsNone(windows_absolute.search(value), path)
                self.assertIsNone(unix_temp.search(value), path)
                self.assertIsNone(temp_segment.search(value), path)
                self.assertNotIn("AppData", value, path)
                self.assertNotIn("python-oracle-index.sqlite3", value, path)

    def test_generator_check_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--check", "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "passed")

    def test_eval_report_preserves_fixture_backed_hard_eval_honesty(self) -> None:
        summary = _load_json("archive_resolution_evals/suite_summary.json")
        full_report = _load_json("archive_resolution_evals/full_report.json")

        self.assertEqual(summary["status_counts"], {"satisfied": 6})
        self.assertEqual(summary["total_task_count"], 6)
        self.assertEqual(full_report["status_counts"], {"satisfied": 6})
        self.assertTrue(
            all(task["overall_status"] == "satisfied" for task in full_report["tasks"])
        )
        article = next(
            task
            for task in full_report["tasks"]
            if task["task_id"] == "article_inside_magazine_scan"
        )
        self.assertEqual(article["overall_status"], "satisfied")
        self.assertIn("article-scan-recorded-fixtures", json.dumps(article, sort_keys=True))
        self.assertIn("ocr_text_fixture", json.dumps(article, sort_keys=True))

    def test_query_planner_outputs_include_expected_task_kinds(self) -> None:
        for filename, expected_task_kind in EXPECTED_TASK_KINDS.items():
            with self.subTest(filename=filename):
                payload = _load_json(f"query_planner/{filename}")
                self.assertEqual(payload["status_code"], 200)
                self.assertEqual(
                    payload["body"]["query_plan"]["task_kind"],
                    expected_task_kind,
                )

    def test_source_registry_outputs_include_fixture_sources(self) -> None:
        sources = _load_json("source_registry/sources_list.json")
        source_ids = {source["source_id"] for source in sources["body"]["sources"]}

        self.assertIn("synthetic-fixtures", source_ids)
        self.assertIn("github-releases-recorded-fixtures", source_ids)
        self.assertIn("internet-archive-recorded-fixtures", source_ids)
        self.assertIn("local-bundle-fixtures", source_ids)
        self.assertIn("article-scan-recorded-fixtures", source_ids)

        synthetic = _load_json("source_registry/source_synthetic_fixtures.json")
        github = _load_json("source_registry/source_github_releases_recorded_fixtures.json")
        internet_archive = _load_json(
            "source_registry/source_internet_archive_recorded_fixtures.json"
        )
        local_bundle = _load_json("source_registry/source_local_bundle_fixtures.json")
        article_scan = _load_json("source_registry/source_article_scan_recorded_fixtures.json")
        self.assertEqual(synthetic["body"]["selected_source_id"], "synthetic-fixtures")
        self.assertEqual(
            github["body"]["selected_source_id"],
            "github-releases-recorded-fixtures",
        )
        self.assertEqual(
            internet_archive["body"]["selected_source_id"],
            "internet-archive-recorded-fixtures",
        )
        self.assertEqual(local_bundle["body"]["selected_source_id"], "local-bundle-fixtures")
        self.assertEqual(
            article_scan["body"]["selected_source_id"],
            "article-scan-recorded-fixtures",
        )

    def test_local_index_fts_mode_is_normalized(self) -> None:
        status = _load_json("local_index/status_after_build.json")
        self.assertEqual(
            status["body"]["index"]["fts_mode"],
            "<PYTHON_ORACLE_FTS_MODE_NORMALIZED>",
        )
        self.assertEqual(
            status["body"]["index"]["index_path"],
            "<PYTHON_ORACLE_LOCAL_INDEX_PATH>",
        )


def _load_json(relative_path: str) -> dict[str, object]:
    path = GOLDEN_ROOT / relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            values.extend(_iter_string_values(item))
        return values
    if isinstance(value, dict):
        values = []
        for item in value.values():
            values.extend(_iter_string_values(item))
        return values
    return []


if __name__ == "__main__":
    unittest.main()
