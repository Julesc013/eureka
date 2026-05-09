import unittest

from runtime.snapshots.consumer import build_snapshot_consumer_report, validate_snapshot_consumer_report
from runtime.snapshots.envelope import build_snapshot_envelope
from runtime.snapshots.fixity import build_snapshot_fixity_report
from runtime.snapshots.manifest import build_snapshot_manifest
from runtime.snapshots.signature import build_unsigned_signature_envelope


class SnapshotConsumerTests(unittest.TestCase):
    def test_snapshot_consumer_loads_fixture_bundle(self):
        records = [{"record_type": "object_record", "canonical_ref": "fixture:object:consumer", "title": "Consumer"}]
        manifest = build_snapshot_manifest(records)
        envelope = build_snapshot_envelope(records)
        fixity = build_snapshot_fixity_report(envelope, manifest)
        signature = build_unsigned_signature_envelope(envelope)
        report = build_snapshot_consumer_report(
            {
                "envelope": envelope,
                "manifest": manifest,
                "fixity": fixity,
                "signature": signature,
            }
        )
        self.assertEqual(validate_snapshot_consumer_report(report), [])
        self.assertEqual(report["consumer_mode"], "local_fixture_offline")
        self.assertEqual(report["records_loaded"], 1)
        self.assertFalse(report["product_boundary"]["enabled_live_access"])


if __name__ == "__main__":
    unittest.main()
