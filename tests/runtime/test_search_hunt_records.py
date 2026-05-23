from __future__ import annotations

import unittest

from runtime.search.hunt import (
    ALLOWED_SEARCH_HUNT_CHECKED_LAYERS,
    ALLOWED_SEARCH_HUNT_STATES,
    ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS,
    SearchHuntSession,
    SearchHuntValidationError,
    validate_no_forbidden_side_effects,
    validate_query_text,
    validate_search_hunt_session,
)


class SearchHuntRecordTests(unittest.TestCase):
    def test_session_validates_required_fields_and_layers(self) -> None:
        session = SearchHuntSession.new("  SampleProject  ")
        validate_search_hunt_session(session)
        self.assertEqual("sampleproject", session.normalized_query)
        self.assertEqual("created", session.state.value)
        self.assertEqual(tuple(ALLOWED_SEARCH_HUNT_CHECKED_LAYERS), session.checked_layers)
        self.assertEqual(tuple(ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS), session.unchecked_layers)
        self.assertIn("created", ALLOWED_SEARCH_HUNT_STATES)

    def test_query_validation_rejects_empty_or_overlong_queries(self) -> None:
        with self.assertRaises(SearchHuntValidationError):
            validate_query_text("   ")
        with self.assertRaises(SearchHuntValidationError):
            validate_query_text("x" * 600)

    def test_forbidden_side_effect_flags_fail_closed(self) -> None:
        with self.assertRaises(SearchHuntValidationError):
            validate_no_forbidden_side_effects({"source_probe_executed": True})
        validate_no_forbidden_side_effects({"source_probe_executed": False})


if __name__ == "__main__":
    unittest.main()
