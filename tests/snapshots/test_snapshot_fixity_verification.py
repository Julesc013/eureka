import unittest

from runtime.snapshots.envelope import build_snapshot_envelope
from runtime.snapshots.fixity import build_snapshot_fixity_report, compute_snapshot_sha256, validate_snapshot_fixity_report
from runtime.snapshots.manifest import build_snapshot_manifest
from runtime.snapshots.signature import (
    build_placeholder_signature_envelope,
    build_snapshot_signature_verification_report,
    build_unsigned_signature_envelope,
    validate_snapshot_signature_envelope,
)
from runtime.snapshots.verify import build_snapshot_verification_report


class SnapshotFixityVerificationTests(unittest.TestCase):
    def _bundle(self):
        records = [{"record_type": "object_record", "canonical_ref": "fixture:object:fixity", "title": "Fixity"}]
        manifest = build_snapshot_manifest(records)
        envelope = build_snapshot_envelope(records)
        return envelope, manifest

    def test_sha256_fixity_is_deterministic(self):
        one = compute_snapshot_sha256({"b": 2, "a": 1})
        two = compute_snapshot_sha256({"a": 1, "b": 2})
        self.assertEqual(one, two)

    def test_fixity_does_not_imply_authenticity(self):
        envelope, manifest = self._bundle()
        report = build_snapshot_fixity_report(envelope, manifest)
        self.assertEqual(validate_snapshot_fixity_report(report), [])
        self.assertFalse(report["truth_boundary"]["fixity_implies_authenticity"])

    def test_unsigned_signature_envelope_validates_as_unsigned(self):
        envelope, _ = self._bundle()
        signature = build_unsigned_signature_envelope(envelope)
        self.assertEqual(validate_snapshot_signature_envelope(signature), [])
        self.assertEqual(signature["signature_status"], "unsigned")
        verification = build_snapshot_signature_verification_report(signature)
        self.assertFalse(verification["private_key_used"])

    def test_placeholder_signature_does_not_imply_trust(self):
        envelope, _ = self._bundle()
        signature = build_placeholder_signature_envelope(envelope)
        self.assertFalse(signature["truth_boundary"]["signature_placeholder_implies_trust"])
        verification = build_snapshot_signature_verification_report(signature)
        self.assertEqual(verification["verification_status"], "unsigned_or_placeholder_only")

    def test_malformed_signature_blocks_verification(self):
        envelope, _ = self._bundle()
        signature = build_unsigned_signature_envelope(envelope)
        signature["signature_status"] = "malformed"
        report = build_snapshot_signature_verification_report(signature)
        self.assertEqual(report["verification_status"], "blocked_malformed_signature_envelope")

    def test_public_and_master_index_claims_rejected(self):
        envelope, manifest = self._bundle()
        envelope["truth_boundary"]["public_index_mutated"] = True
        report = build_snapshot_verification_report({"envelope": envelope, "manifest": manifest})
        self.assertTrue(report["blockers"])

    def test_rights_malware_installability_claims_rejected(self):
        envelope, manifest = self._bundle()
        manifest["truth_boundary"]["rights_clearance_claimed"] = True
        report = build_snapshot_verification_report({"envelope": envelope, "manifest": manifest})
        self.assertTrue(report["blockers"])

    def test_download_mirror_execute_claims_rejected(self):
        envelope, manifest = self._bundle()
        manifest["truth_boundary"]["snapshot_downloads_files"] = True
        report = build_snapshot_verification_report({"envelope": envelope, "manifest": manifest})
        self.assertTrue(report["blockers"])


if __name__ == "__main__":
    unittest.main()
