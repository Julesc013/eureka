from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.extraction_safe_fixtures import build_member_manifest, validate_member_record


REPO_ROOT = Path(__file__).resolve().parents[2]


class F0MemberManifestTests(unittest.TestCase):
    def load_descriptor(self, rel: str) -> dict:
        return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))

    def test_path_traversal_member_is_blocked(self) -> None:
        manifest = build_member_manifest(self.load_descriptor("examples/f0/unsafe_path_traversal_descriptor.json"))
        reasons = set(manifest["risk_report"]["blocked_reasons"])
        self.assertIn("path_traversal", reasons)
        self.assertTrue(any(member["blocked"] for member in manifest["members"]))

    def test_absolute_path_member_is_blocked(self) -> None:
        manifest = build_member_manifest(self.load_descriptor("examples/f0/unsafe_absolute_path_descriptor.json"))
        reasons = set(manifest["risk_report"]["blocked_reasons"])
        self.assertIn("absolute_path", reasons)

    def test_member_record_validator_matches_path_safety(self) -> None:
        manifest = build_member_manifest(self.load_descriptor("examples/f0/unsafe_path_traversal_descriptor.json"))
        for member in manifest["members"]:
            report = validate_member_record(member)
            self.assertEqual(report["status"], "valid", report["errors"])


if __name__ == "__main__":
    unittest.main()
