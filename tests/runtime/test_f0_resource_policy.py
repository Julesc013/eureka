from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.extraction_safe_fixtures import build_member_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


class F0ResourcePolicyTests(unittest.TestCase):
    def test_excessive_declared_size_is_blocked(self) -> None:
        descriptor = json.loads((REPO_ROOT / "examples/f0/large_member_declared_size_descriptor.json").read_text(encoding="utf-8"))
        manifest = build_member_manifest(descriptor)
        self.assertIn("declared_size_exceeds_limit", manifest["risk_report"]["blocked_reasons"])

    def test_unknown_container_is_blocked_or_deferred(self) -> None:
        descriptor = {
            "container_id": "test_unknown",
            "fixture_id": "unknown",
            "container_kind": "unknown_binary_container",
            "locator": "descriptor-only:unknown"
        }
        manifest = build_member_manifest(descriptor)
        self.assertIn("container_type_blocked_or_deferred", manifest["risk_flags"])


if __name__ == "__main__":
    unittest.main()
