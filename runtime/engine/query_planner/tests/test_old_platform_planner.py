from __future__ import annotations

import unittest

from runtime.engine.query_planner import plan_query


class OldPlatformPlannerTestCase(unittest.TestCase):
    def test_windows_7_apps_treats_os_as_platform_constraint(self) -> None:
        task = plan_query("Windows 7 apps")

        self.assertEqual(task.task_kind, "browse_software")
        self.assertEqual(task.object_type, "software")
        self.assertEqual(task.constraints["platform"]["family"], "Windows NT")
        self.assertEqual(task.constraints["platform"]["version"], "6.1")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows 7")
        self.assertTrue(task.constraints["platform_is_constraint"])
        self.assertIn("operating_system_install_media", task.exclude)
        self.assertIn("os_iso_image", task.exclude)

    def test_windows_nt_61_utilities_normalizes_to_windows_7(self) -> None:
        task = plan_query("Windows NT 6.1 utilities")

        self.assertEqual(task.task_kind, "browse_software")
        self.assertEqual(task.object_type, "software")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows 7")
        self.assertEqual(task.constraints["function_hint"], "utility")

    def test_windows_xp_software_is_platform_scoped_software(self) -> None:
        task = plan_query("Windows XP software")

        self.assertEqual(task.task_kind, "browse_software")
        self.assertEqual(task.constraints["platform"]["version"], "5.1")
        self.assertEqual(task.constraints["target_object_hint"], "software_for_platform")

    def test_windows_98_registry_repair_is_uncertain_software_identity(self) -> None:
        task = plan_query("Windows 98 registry repair")

        self.assertEqual(task.task_kind, "identify_software")
        self.assertEqual(task.object_type, "software")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows 98")
        self.assertEqual(task.constraints["function_hint"], "registry repair")
        self.assertIn("uncertainty_notes", task.constraints)

    def test_latest_firefox_before_xp_support_ended_records_temporal_goal(self) -> None:
        task = plan_query("latest Firefox before XP support ended")

        self.assertEqual(task.task_kind, "find_latest_compatible_release")
        self.assertEqual(task.object_type, "software_release")
        self.assertEqual(task.constraints["product_hint"], "Firefox")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows XP")
        self.assertEqual(task.constraints["temporal_goal"], "latest_before_support_drop")
        self.assertIn("compare_versions", task.action_hints)

    def test_latest_vlc_for_windows_xp_records_latest_compatible_goal(self) -> None:
        task = plan_query("latest VLC for Windows XP")

        self.assertEqual(task.task_kind, "find_latest_compatible_release")
        self.assertEqual(task.constraints["product_hint"], "VLC")
        self.assertEqual(task.constraints["temporal_goal"], "latest_compatible")

    def test_driver_for_thinkpad_t42_wifi_windows_2000(self) -> None:
        task = plan_query("driver for ThinkPad T42 Wi-Fi Windows 2000")

        self.assertEqual(task.task_kind, "find_driver")
        self.assertEqual(task.object_type, "driver")
        self.assertEqual(task.constraints["hardware_hint"], "ThinkPad T42 Wi-Fi")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows 2000")
        self.assertIn("INF", task.constraints["representation_hints"])
        self.assertTrue(task.constraints["member_discovery_hints"]["prefer_inf_member"])

    def test_creative_ct1740_driver_windows_98(self) -> None:
        task = plan_query("Creative CT1740 driver Windows 98")

        self.assertEqual(task.task_kind, "find_driver")
        self.assertEqual(task.constraints["hardware_hint"], "Creative CT1740")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Windows 98")

    def test_old_blue_ftp_client_for_xp_remains_uncertain(self) -> None:
        task = plan_query("old blue FTP client for XP")

        self.assertEqual(task.task_kind, "identify_software")
        self.assertEqual(task.object_type, "software")
        self.assertEqual(task.constraints["function_hint"], "FTP client")
        self.assertEqual(task.constraints["descriptor_hint"], "blue")
        self.assertIn("Vague identity query", task.planner_notes[0])

    def test_driver_inside_support_cd_records_member_discovery(self) -> None:
        task = plan_query("driver inside support CD")

        self.assertEqual(task.task_kind, "find_member_in_container")
        self.assertEqual(task.object_type, "package_member")
        self.assertEqual(task.constraints["container_hint"], "support_cd")
        self.assertEqual(task.constraints["member_type_hint"], "driver")
        self.assertIn("decompose", task.action_hints)
        self.assertTrue(task.constraints["member_discovery_hints"]["preserve_parent_lineage"])

    def test_installer_inside_iso_records_container_hint(self) -> None:
        task = plan_query("installer inside ISO")

        self.assertEqual(task.task_kind, "find_member_in_container")
        self.assertEqual(task.constraints["container_hint"], "ISO")
        self.assertEqual(task.constraints["member_type_hint"], "installer")

    def test_manual_for_sound_blaster_ct1740(self) -> None:
        task = plan_query("manual for Sound Blaster CT1740")

        self.assertEqual(task.task_kind, "find_documentation")
        self.assertEqual(task.object_type, "documentation")
        self.assertEqual(task.constraints["product_hint"], "Sound Blaster CT1740")
        self.assertIn("PDF", task.constraints["representation_hints"])

    def test_mac_os_9_browser_is_platform_software(self) -> None:
        task = plan_query("Mac OS 9 browser")

        self.assertEqual(task.task_kind, "browse_software")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Mac OS 9")
        self.assertEqual(task.constraints["function_hint"], "browser")

    def test_powerpc_mac_os_x_tiger_browser_records_architecture(self) -> None:
        task = plan_query("PowerPC Mac OS X 10.4 browser")

        self.assertEqual(task.task_kind, "browse_software")
        self.assertEqual(task.constraints["platform"]["marketing_alias"], "Mac OS X Tiger")
        self.assertEqual(task.constraints["platform"]["architecture"], "PowerPC")


if __name__ == "__main__":
    unittest.main()
