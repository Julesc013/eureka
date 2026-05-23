from __future__ import annotations

import unittest

from runtime.search.hunt import SearchHuntSession, SearchHuntTransitionError, SearchHuntState, apply_transition, validate_transition


class SearchHuntTransitionTests(unittest.TestCase):
    def test_required_valid_transitions_pass(self) -> None:
        cases = (
            ("created", "running"),
            ("created", "paused"),
            ("created", "blocked"),
            ("created", "cancelled"),
            ("running", "paused"),
            ("running", "waiting_for_user"),
            ("running", "waiting_for_policy"),
            ("running", "complete"),
            ("running", "failed"),
            ("running", "blocked"),
            ("running", "cancelled"),
            ("paused", "running"),
            ("paused", "cancelled"),
            ("waiting_for_user", "running"),
            ("waiting_for_user", "cancelled"),
            ("waiting_for_policy", "running"),
            ("waiting_for_policy", "blocked"),
            ("waiting_for_policy", "cancelled"),
            ("blocked", "running"),
            ("blocked", "cancelled"),
            ("failed", "running"),
            ("complete", "complete"),
            ("cancelled", "cancelled"),
        )
        for current, target in cases:
            with self.subTest(current=current, target=target):
                self.assertEqual(target, validate_transition(current, target).value)

    def test_invalid_transition_fails_closed(self) -> None:
        with self.assertRaises(SearchHuntTransitionError):
            validate_transition("created", "complete")

    def test_apply_transition_updates_state_and_terminal_repeat_is_idempotent(self) -> None:
        session = SearchHuntSession.new("sampleproject")
        running = apply_transition(session, "running", "start")
        self.assertEqual(SearchHuntState.RUNNING, running.state)
        complete = apply_transition(running, "complete", "done")
        repeated = apply_transition(complete, "complete", "repeat")
        self.assertIs(repeated, complete)


if __name__ == "__main__":
    unittest.main()
