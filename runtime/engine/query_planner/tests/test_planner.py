from __future__ import annotations

import unittest

from runtime.engine.query_planner import derive_search_query_from_task, plan_query


class QueryPlannerTestCase(unittest.TestCase):
    def test_windows_7_apps(self) -> None:
        task = plan_query("Windows 7 apps")

        self.assertEqual(task.task_kind, "browse_software")
        self.assertEqual(task.object_type, "software")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows 7")
        self.assertIn("direct_software_artifact", task.prefer)
        self.assertIn("operating_system_image", task.exclude)

    def test_old_blue_ftp_client_for_xp(self) -> None:
        task = plan_query("old blue FTP client for XP")

        self.assertEqual(task.task_kind, "identify_software")
        self.assertEqual(task.object_type, "software")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows XP")
        self.assertEqual(task.constraints["function_hint"], "FTP client")
        self.assertEqual(task.constraints["descriptor_hint"], "blue")
        self.assertIn("uncertainty_notes", task.constraints)

    def test_latest_firefox_before_xp_support_ended(self) -> None:
        task = plan_query("latest Firefox before XP support ended")

        self.assertEqual(task.task_kind, "find_latest_compatible_release")
        self.assertEqual(task.object_type, "software_release")
        self.assertEqual(task.constraints["product_hint"], "Firefox")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows XP")
        self.assertEqual(task.constraints["temporal_goal"], "latest_before_support_drop")
        self.assertEqual(derive_search_query_from_task(task), "Firefox")

    def test_driver_for_thinkpad_t42(self) -> None:
        task = plan_query("driver for ThinkPad T42 Wi-Fi Windows 2000")

        self.assertEqual(task.task_kind, "find_driver")
        self.assertEqual(task.object_type, "driver")
        self.assertEqual(task.constraints["hardware_hint"], "ThinkPad T42 Wi-Fi")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows 2000")

    def test_article_inside_magazine_scan(self) -> None:
        task = plan_query("article about ray tracing in a 1994 magazine")

        self.assertEqual(task.task_kind, "find_document_article")
        self.assertEqual(task.object_type, "document_article")
        self.assertEqual(task.constraints["topic_hint"], "ray tracing")
        self.assertEqual(task.constraints["date_year_hint"], "1994")
        self.assertIn("article_member", task.prefer)

    def test_unknown_query_falls_back_to_generic_search(self) -> None:
        task = plan_query("mysterious thing")

        self.assertEqual(task.task_kind, "generic_search")
        self.assertEqual(task.object_type, "unknown")
        self.assertEqual(task.planner_confidence, "low")


if __name__ == "__main__":
    unittest.main()
