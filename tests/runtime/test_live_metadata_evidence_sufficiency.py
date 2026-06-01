from __future__ import annotations

import unittest

from runtime.review.live_metadata import (
    assess_live_metadata_evidence_sufficiency,
    load_live_metadata_candidates,
)


class LiveMetadataEvidenceSufficiencyTests(unittest.TestCase):
    def test_sufficiency_never_supports_verified_download(self) -> None:
        for candidate in load_live_metadata_candidates():
            sufficiency = assess_live_metadata_evidence_sufficiency(candidate)

            self.assertEqual("live_metadata_evidence_sufficiency.v0", sufficiency["schema_version"])
            self.assertTrue(sufficiency["review_required"])
            self.assertFalse(sufficiency["supports_verified_download"])
            self.assertFalse(sufficiency["accepted_truth"])
            self.assertFalse(sufficiency["download_claim"])
            self.assertFalse(sufficiency["malware_clean_claim"])
            self.assertFalse(sufficiency["rights_clearance_claim"])


if __name__ == "__main__":
    unittest.main()
