import unittest

from runtime.seed_batches import approval_template, validate_live_metadata_pilot_approval


class LiveMetadataPilotApprovalTests(unittest.TestCase):
    def test_approval_template_has_required_phrase_and_boundaries(self):
        template = approval_template()

        self.assertEqual(template["approval_phrase"], "RUN_BOUNDED_LIVE_METADATA_PILOT")
        self.assertFalse(template["raw_response_commit_allowed"])
        self.assertFalse(template["downloads_allowed"])
        self.assertIn("review_required", template["acknowledged_boundaries"])

    def test_blank_template_is_not_verified(self):
        result = validate_live_metadata_pilot_approval(approval_template())

        self.assertFalse(result["approval_verified"])
        self.assertIn("max_total_requests", result)


if __name__ == "__main__":
    unittest.main()
