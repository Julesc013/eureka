from __future__ import annotations

from pathlib import Path
import unittest

from runtime.local_eval.domain_packs import REQUIRED_DOMAIN_IDS, load_domain_packs_from_manifest, map_domain_to_syn_cases


REPO_ROOT = Path(__file__).resolve().parents[2]


class DomainSynIntegrationTests(unittest.TestCase):
    def test_each_domain_maps_to_syn_cases_without_creating_truth(self) -> None:
        packs = load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")
        self.assertEqual({pack["domain_id"] for pack in packs}, set(REQUIRED_DOMAIN_IDS))
        for pack in packs:
            mapping = map_domain_to_syn_cases(pack)
            with self.subTest(domain_id=pack["domain_id"]):
                self.assertGreaterEqual(mapping["syn_case_count"], 2)
                self.assertFalse(mapping["creates_runtime_query_logs"])
                self.assertFalse(mapping["creates_evidence"])

    def test_frontier_and_legacy_prompt_examples_are_preserved(self) -> None:
        packs = {pack["domain_id"]: pack for pack in load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")}
        frontier_queries = {ref["query_text"] for ref in packs["frontier_resolution_media"]["syn_case_refs"]}
        legacy_queries = {ref["query_text"] for ref in packs["legacy_software"]["syn_case_refs"]}
        self.assertIn("New York 1993 D-Theater HD demo tape original source", frontier_queries)
        self.assertIn("Windows 7-compatible portable utilities, not Windows 7 ISO", legacy_queries)


if __name__ == "__main__":
    unittest.main()
