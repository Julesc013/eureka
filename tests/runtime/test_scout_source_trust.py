from __future__ import annotations

import unittest

from runtime.scout import build_source_trust_observation, load_candidate_index_from_examples


class ScoutSourceTrustTest(unittest.TestCase):
    def test_source_trust_observation_does_not_claim_verification(self) -> None:
        candidates = load_candidate_index_from_examples()["candidates"]
        observation = build_source_trust_observation(candidates)

        self.assertEqual(observation["observation_kind"], "candidate_source_family_cluster")
        self.assertEqual(observation["observation_value"]["accepted_evidence_count"], 0)
        self.assertFalse(observation["observation_value"]["live_verified"])
        self.assertFalse(observation["accepted_truth"])
        self.assertFalse(observation["live_source_call_performed"])


if __name__ == "__main__":
    unittest.main()
