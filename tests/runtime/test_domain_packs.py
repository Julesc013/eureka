from __future__ import annotations

from pathlib import Path
import unittest

from runtime.local.eval.domain_packs import (
    BLOCKED_ACTIONS,
    REQUIRED_DOMAIN_IDS,
    load_domain_packs_from_manifest,
    validate_domain_pack,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class DomainPackRuntimeTests(unittest.TestCase):
    def test_seed_manifest_loads_all_required_domains(self) -> None:
        packs = load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")
        self.assertEqual({pack["domain_id"] for pack in packs}, set(REQUIRED_DOMAIN_IDS))

    def test_domain_packs_validate(self) -> None:
        packs = load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")
        for pack in packs:
            with self.subTest(domain_id=pack["domain_id"]):
                report = validate_domain_pack(pack)
                self.assertEqual(report["status"], "valid", report["errors"])

    def test_action_defaults_block_unsafe_actions(self) -> None:
        packs = load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")
        for pack in packs:
            blocked = set(pack["action_posture_defaults"]["blocked_actions"])
            with self.subTest(domain_id=pack["domain_id"]):
                self.assertTrue(set(BLOCKED_ACTIONS).issubset(blocked))
                self.assertFalse(pack["non_claims"]["evidence_created"])
                self.assertFalse(pack["non_claims"]["reviewed_record_created"])


if __name__ == "__main__":
    unittest.main()
