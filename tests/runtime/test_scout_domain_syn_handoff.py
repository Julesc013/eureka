from __future__ import annotations

from pathlib import Path
import unittest

from runtime.local_eval.domain_packs import load_domain_packs_from_manifest
from runtime.local_eval.scout_schema import (
    REQUIRED_DOMAIN_IDS,
    load_scout_seed_records,
    map_scout_seed_to_domain,
    map_scout_seed_to_syn_case,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class ScoutDomainSynHandoffTests(unittest.TestCase):
    def test_domain_handoff_maps_all_required_domains(self) -> None:
        domain_packs = {
            pack["domain_id"]: pack
            for pack in load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")
        }
        self.assertEqual(set(domain_packs), set(REQUIRED_DOMAIN_IDS))
        seeds = load_scout_seed_records(REPO_ROOT / "examples/scout/scout_seed_manifest.json")
        for seed in seeds:
            with self.subTest(seed_id=seed["seed_id"]):
                mapping = map_scout_seed_to_domain(seed, domain_packs[seed["domain_id"]])
                self.assertEqual(mapping["domain_id"], seed["domain_id"])
                self.assertFalse(mapping["creates_evidence"])
                self.assertFalse(mapping["creates_runtime_workunit"])

    def test_syn_handoff_does_not_create_fake_evidence(self) -> None:
        seeds = load_scout_seed_records(REPO_ROOT / "examples/scout/scout_seed_manifest.json")
        for seed in seeds:
            mapping = map_scout_seed_to_syn_case(seed)
            with self.subTest(seed_id=seed["seed_id"]):
                self.assertEqual(mapping["query_text"], seed["query_text"])
                self.assertFalse(mapping["creates_evidence"])
                self.assertFalse(mapping["creates_runtime_query"])
                self.assertTrue(mapping["review_required"])


if __name__ == "__main__":
    unittest.main()
