from __future__ import annotations

from pathlib import Path
import unittest

from runtime.local.eval.domain_packs import compile_domain_query_hints, load_domain_packs_from_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


class DomainQueryHintTests(unittest.TestCase):
    def test_query_hints_compile_promote_suppress_and_sources(self) -> None:
        packs = load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")
        for pack in packs:
            hints = compile_domain_query_hints(pack)
            with self.subTest(domain_id=pack["domain_id"]):
                self.assertTrue(hints["promote_terms"])
                self.assertTrue(hints["suppress_terms"])
                self.assertTrue(hints["source_family_preferences"])
                self.assertFalse(hints["creates_runtime_behavior"])

    def test_required_domain_examples_are_present(self) -> None:
        packs = {pack["domain_id"]: pack for pack in load_domain_packs_from_manifest(REPO_ROOT / "examples/domain/domain_seed_manifest.json")}
        legacy = packs["legacy_software"]["query_hints"][0]
        self.assertIn("portable app", legacy["promote_terms"])
        self.assertIn("OS ISO when user wants apps", legacy["suppress_terms"])

        driver = packs["driver_support_media"]["query_hints"][0]
        self.assertIn("generic driver updater sites", driver["suppress_terms"])

        package = packs["package_source_release"]["query_hints"][0]
        self.assertIn("DirectX SDK June 2010 offline installer", [ref["query_text"] for ref in packs["package_source_release"]["syn_case_refs"]])


if __name__ == "__main__":
    unittest.main()
