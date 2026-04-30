from __future__ import annotations

import unittest

from runtime.engine.evals.search_usefulness_runner import build_default_search_usefulness_audit_runner


SELECTED_TARGETS = {
    "archived_firefox_xp_release_notes",
    "archived_microsoft_download_center_directx_90c",
    "old_creative_labs_driver_page",
    "old_netscape_download_page",
    "software_heritage_snapshot_old_project",
    "visual_cpp_6_sp_readme",
    "visual_cpp_6_service_pack_download",
    "manual_sound_blaster_ct1740",
    "sound_blaster_live_manual",
    "thinkpad_t42_hardware_maintenance_manual",
    "windows_98_resource_kit_pdf",
    "windows_2000_antivirus",
    "last_chrome_for_windows_xp",
    "last_itunes_for_windows_xp",
    "classic_windows_file_transfer_blue_globe",
}


class SearchUsefulnessSourceExpansionV2EvalTestCase(unittest.TestCase):
    def test_selected_source_gap_targets_have_rank_one_fixture_evidence(self) -> None:
        result = build_default_search_usefulness_audit_runner().run_suite()
        by_id = {item.query_id: item for item in result.task_results}

        self.assertGreaterEqual(set(by_id), SELECTED_TARGETS)
        for query_id in sorted(SELECTED_TARGETS):
            with self.subTest(query_id=query_id):
                item = by_id[query_id]
                self.assertEqual(item.eureka_status, "partial")
                self.assertEqual(item.first_useful_result_rank, 1)
                self.assertGreater(item.search_result_count, 0)

    def test_source_expansion_v2_counts_remain_honest(self) -> None:
        result = build_default_search_usefulness_audit_runner().run_suite()

        self.assertEqual(result.total_query_count, 64)
        self.assertEqual(
            result.eureka_status_counts,
            {
                "capability_gap": 7,
                "covered": 5,
                "partial": 40,
                "source_gap": 10,
                "unknown": 2,
            },
        )
        self.assertEqual(result.external_baseline_pending_counts["google"], 64)
        self.assertEqual(result.external_baseline_pending_counts["internet_archive_metadata"], 64)
        self.assertEqual(result.external_baseline_pending_counts["internet_archive_full_text"], 64)


if __name__ == "__main__":
    unittest.main()
