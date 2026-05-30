from __future__ import annotations

import unittest

from runtime.candidate_store import build_candidate_fingerprint, sample_candidate_index


class CandidateFingerprintTest(unittest.TestCase):
    def test_fingerprint_is_deterministic(self) -> None:
        candidate = sample_candidate_index()["candidates"][0]
        first = build_candidate_fingerprint(candidate)
        second = build_candidate_fingerprint(candidate)

        self.assertEqual(first["dedupe_key"], second["dedupe_key"])
        self.assertEqual(first["candidate_id"], candidate["candidate_id"])
        self.assertTrue(first["normalized_title"])


if __name__ == "__main__":
    unittest.main()
