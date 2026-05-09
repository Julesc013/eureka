import unittest

from runtime.snapshots.envelope import build_snapshot_envelope, validate_snapshot_envelope
from runtime.snapshots.manifest import build_snapshot_manifest, build_snapshot_record, validate_snapshot_manifest, validate_snapshot_record


class SnapshotEnvelopeManifestTests(unittest.TestCase):
    def test_minimal_snapshot_manifest_builds(self):
        manifest = build_snapshot_manifest(
            [
                {
                    "record_type": "object_record",
                    "canonical_ref": "fixture:object:minimal",
                    "title": "Minimal Object",
                    "summary": "Fixture object.",
                }
            ]
        )
        self.assertEqual(manifest["schema_version"], "snapshot_manifest.v0")
        self.assertEqual(manifest["record_count"], 1)
        self.assertEqual(validate_snapshot_manifest(manifest), [])

    def test_search_snapshot_manifest_builds(self):
        manifest = build_snapshot_manifest(
            [
                {
                    "record_type": "search_result",
                    "canonical_ref": "fixture:search:one",
                    "title": "Search Result",
                    "summary": "Fixture search result.",
                }
            ]
        )
        self.assertEqual(manifest["record_type_counts"]["search_result"], 1)
        self.assertIn("text", manifest["render_targets"])

    def test_object_snapshot_manifest_builds(self):
        envelope = build_snapshot_envelope(
            [
                {
                    "record_type": "object_record",
                    "canonical_ref": "fixture:object:one",
                    "title": "Object",
                    "summary": "Fixture object.",
                }
            ]
        )
        self.assertEqual(validate_snapshot_envelope(envelope), [])
        self.assertFalse(envelope["product_boundary"]["enabled_relay"])

    def test_action_manifest_snapshot_record_builds(self):
        record = build_snapshot_record(
            {
                "record_type": "action_manifest",
                "canonical_ref": "fixture:action:view",
                "title": "View",
                "summary": "Safe descriptive action.",
                "blocked_actions": ["download", "execute"],
            }
        )
        self.assertEqual(record["record_type"], "action_manifest")
        self.assertIn("download", record["render_fields"]["blocked_actions"])
        self.assertEqual(validate_snapshot_record(record), [])

    def test_known_absence_snapshot_record_builds(self):
        record = build_snapshot_record(
            {
                "record_type": "known_absence",
                "canonical_ref": "fixture:absence:local",
                "title": "No reviewed fixture result",
                "summary": "Local fixture absence only.",
            }
        )
        self.assertEqual(record["record_type"], "known_absence")
        self.assertIn("no accepted public truth", record["render_fields"]["no_claims"])

    def test_policy_blocked_snapshot_record_builds(self):
        record = build_snapshot_record(
            {
                "record_type": "policy_blocked_record",
                "canonical_ref": "fixture:blocked:relay",
                "title": "Relay blocked",
                "summary": "Relay is not enabled.",
                "blocked_actions": ["relay", "hosting"],
            }
        )
        self.assertEqual(record["record_status"], "policy_blocked")
        self.assertIn("relay", record["render_fields"]["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
