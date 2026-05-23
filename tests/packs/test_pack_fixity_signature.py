from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from runtime.local.foundry import pack_fixity, pack_quarantine, pack_signature


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class PackFixitySignatureTests(unittest.TestCase):
    def test_sha256_fixity_is_deterministic(self) -> None:
        pack = load_json("examples/packs/exports/evidence_pack_export_v0.json")
        first = pack_fixity.build_pack_fixity_report(pack)
        second = pack_fixity.build_pack_fixity_report(pack)
        self.assertEqual(first["hash_value"], second["hash_value"])
        self.assertEqual(first["hash_algorithm"], "sha256")
        self.assertEqual(pack_fixity.validate_pack_fixity_report(first), [])

    def test_fixity_does_not_imply_authenticity(self) -> None:
        report = pack_fixity.build_pack_fixity_report(load_json("examples/packs/exports/evidence_pack_export_v0.json"))
        self.assertFalse(report["truth_boundary"]["fixity_implies_authenticity"])
        bad = copy.deepcopy(report)
        bad["truth_boundary"]["fixity_implies_authenticity"] = True
        self.assertTrue(any("fixity_implies_authenticity" in error for error in pack_fixity.validate_pack_fixity_report(bad)))

    def test_unsigned_pack_produces_needs_review_status(self) -> None:
        envelope = pack_signature.parse_pack_signature_envelope({"pack_export_id": "pack.unsigned.test.v0", "signature_envelope": load_json("examples/packs/quarantine/signatures/unsigned_pack_signature_envelope_v0.json")})
        report = pack_signature.build_signature_verification_report(envelope)
        self.assertEqual(report["verification_status"], "unsigned_needs_review")
        self.assertFalse(report["verification_performed"])

    def test_placeholder_signature_envelope_validates_as_placeholder_only(self) -> None:
        envelope = load_json("examples/packs/quarantine/signatures/placeholder_signature_envelope_v0.json")
        self.assertEqual(envelope["signature_status"], "placeholder_only")
        self.assertEqual(pack_signature.validate_signature_envelope(envelope), [])
        report = pack_signature.build_signature_verification_report(envelope)
        self.assertEqual(report["verification_status"], "placeholder_only")

    def test_malformed_signature_envelope_blocks_acceptance(self) -> None:
        envelope = load_json("examples/packs/quarantine/signatures/malformed_signature_envelope_v0.json")
        report = pack_signature.build_signature_verification_report(envelope)
        self.assertEqual(report["verification_status"], "malformed_envelope")
        pack = load_json("examples/packs/exports/evidence_pack_export_v0.json")
        result = pack_quarantine.build_pack_quarantine_result(pack, {"signature_verification_report": report})
        self.assertEqual(result["quarantine_status"], "blocked_by_signature_policy")

    def test_private_key_input_is_rejected(self) -> None:
        pack = load_json("examples/packs/exports/evidence_pack_export_v0.json")
        bad = copy.deepcopy(pack)
        bad["signature_envelope"] = {"private_key": "fixture"}
        result = pack_quarantine.build_full_quarantine_bundle(bad)["quarantine_result"]
        self.assertTrue(any("private key" in blocker.lower() for blocker in result["blocker_summary"]["blockers"]))

    def test_real_signing_claim_is_rejected(self) -> None:
        envelope = load_json("examples/packs/quarantine/signatures/placeholder_signature_envelope_v0.json")
        report = pack_signature.build_signature_verification_report(envelope)
        bad = copy.deepcopy(report)
        bad["real_signature_created"] = True
        self.assertTrue(any("real_signature_created" in error for error in pack_signature.validate_signature_verification_report(bad)))


if __name__ == "__main__":
    unittest.main()
