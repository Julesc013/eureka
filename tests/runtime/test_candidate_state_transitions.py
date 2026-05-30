from __future__ import annotations

import unittest

from runtime.candidate_store import update_candidate_state


class CandidateStateTransitionTest(unittest.TestCase):
    def test_allows_automatic_transition(self) -> None:
        result = update_candidate_state(
            "candidate-1",
            "seen",
            {"actor_type": "system", "current_state": "new"},
        )
        self.assertTrue(result["transition_allowed"])
        self.assertFalse(result["accepted_truth_created"])

    def test_blocks_public_mutation(self) -> None:
        with self.assertRaises(PermissionError):
            update_candidate_state(
                "candidate-1",
                "useful_lead",
                {"actor_type": "public", "current_state": "needs_review"},
            )

    def test_allows_operator_review_transition_with_approval(self) -> None:
        result = update_candidate_state(
            "candidate-1",
            "useful_lead",
            {"actor_type": "operator", "current_state": "needs_review", "operator_approved": True},
        )
        self.assertEqual(result["new_state"], "useful_lead")
        self.assertFalse(result["public_mutation_enabled"])


if __name__ == "__main__":
    unittest.main()
