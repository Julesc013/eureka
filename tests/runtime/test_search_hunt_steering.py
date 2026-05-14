from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.search_hunt import SearchHuntSession, SearchHuntStore


class SearchHuntSteeringTests(unittest.TestCase):
    def test_steering_preference_recorded_and_deactivated_not_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with SearchHuntStore.open(Path(tmp) / "search_hunt.sqlite") as store:
                store.init()
                hunt = store.create_session(SearchHuntSession.new("sampleproject"))
                preference = store.add_steering_preference(
                    hunt.id,
                    "prefer_official_sources",
                    reason="operator preference",
                    operator_label="tester",
                )
                self.assertTrue(preference.active)
                self.assertEqual(1, len(store.list_steering_preferences(hunt.id)))

                deactivated = store.remove_steering_preference(hunt.id, preference.id, reason="changed")
                self.assertFalse(deactivated.active)
                self.assertEqual([], store.list_steering_preferences(hunt.id))
                all_preferences = store.list_steering_preferences(hunt.id, active_only=False)
                self.assertEqual([preference.id], [item.id for item in all_preferences])
                self.assertEqual(["prefer_official_sources", "remove_steering_preference"], [item.command_type for item in store.list_commands(hunt.id)])

    def test_all_required_steering_types_are_supported(self) -> None:
        expected = (
            "include_source_family",
            "exclude_source_family",
            "prefer_official_sources",
            "allow_community_sources",
            "metadata_only",
            "allow_extraction_future",
            "disallow_extraction",
            "allow_ai_escalation_future",
            "disallow_ai_escalation",
            "add_note",
            "set_priority",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with SearchHuntStore.open(Path(tmp) / "search_hunt.sqlite") as store:
                store.init()
                hunt = store.create_session(SearchHuntSession.new("sampleproject"))
                for item in expected:
                    store.add_steering_preference(hunt.id, item, value="demo", reason="coverage")
                self.assertCountEqual(expected, [item.command_type for item in store.list_steering_preferences(hunt.id)])


if __name__ == "__main__":
    unittest.main()
