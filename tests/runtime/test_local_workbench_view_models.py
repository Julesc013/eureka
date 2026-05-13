from __future__ import annotations

import unittest

from runtime.local_workbench import (
    build_absence_page_view,
    build_home_page_view,
    build_object_page_view,
    build_search_page_view,
    build_source_page_view,
    build_status_page_view,
)


class LocalWorkbenchViewModelTests(unittest.TestCase):
    def test_home_view_uses_status_summary(self) -> None:
        view = build_home_page_view(
            {
                "status": "pass",
                "runtime": {"instance_id": "instance-1", "instance_schema_version": "1"},
                "public_index": {"record_count": 3},
                "warnings": ["sample warning"],
                "limitations": ["local reviewed index only"],
            }
        )
        self.assertEqual("instance-1", view.instance_id)
        self.assertEqual(3, view.record_count)
        self.assertEqual(("sample warning",), view.warnings)

    def test_search_view_contains_presentation_data_only(self) -> None:
        view = build_search_page_view("demo", {"result_count": 1, "results": [{"record_id": "r1"}]})
        self.assertEqual("demo", view.query)
        self.assertEqual(1, view.result_count)
        self.assertEqual("r1", view.results[0]["record_id"])
        self.assertFalse(hasattr(view, "store"))
        self.assertFalse(hasattr(view, "mutate"))

    def test_object_view_has_found_and_not_found_states(self) -> None:
        found = build_object_page_view("r1", {"record_id": "r1", "title": "Demo"})
        missing = build_object_page_view("r2", None)
        self.assertTrue(found.found)
        self.assertFalse(missing.found)

    def test_source_view_defaults_to_empty_records(self) -> None:
        view = build_source_page_view("source-1", {"result_count": 0})
        self.assertEqual("source-1", view.source_id)
        self.assertEqual((), view.records)

    def test_absence_view_does_not_overclaim(self) -> None:
        view = build_absence_page_view("missing", {"absence": {"result_count": 0, "checked_sources": ["public_index"]}})
        self.assertIn("This is local current-index absence only, not global proof.", view.limitations)

    def test_status_view_keeps_disabled_runtime_flags(self) -> None:
        view = build_status_page_view(
            {
                "runtime": {
                    "instance_id": "instance-1",
                    "instance_schema_version": "1",
                    "stores": {},
                    "migration_needed": False,
                    "server_enabled": False,
                    "lan_enabled": False,
                    "deployment_performed": False,
                },
                "warnings": [],
                "limitations": [],
            }
        )
        self.assertFalse(view.server_enabled)
        self.assertFalse(view.lan_enabled)
        self.assertFalse(view.deployment_performed)


if __name__ == "__main__":
    unittest.main()
