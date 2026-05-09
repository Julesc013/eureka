from __future__ import annotations

import copy
import unittest

from runtime.actions.citation_bundle import build_citation_bundle, validate_citation_bundle
from runtime.actions.export_manifest import build_export_manifest, validate_export_manifest
from runtime.actions.preservation_manifest import build_preservation_manifest, validate_preservation_manifest


class CitationExportPreservationTests(unittest.TestCase):
    def test_citation_bundle_preserves_limitations(self) -> None:
        bundle = build_citation_bundle({"subject_ref": "candidate.example.v0", "source_refs": ["source.v0"]})
        self.assertTrue(bundle["limitations"])
        self.assertFalse(bundle["truth_boundary"]["citation_bundle_accepts_truth"])
        self.assertEqual(validate_citation_bundle(bundle), [])

    def test_export_manifest_does_not_import_submit_or_mutate_indexes(self) -> None:
        manifest = build_export_manifest({"subject_ref": "candidate.example.v0"})
        self.assertFalse(manifest["truth_boundary"]["export_manifest_imports_or_submits"])
        self.assertFalse(manifest["truth_boundary"]["public_index_mutated"])
        self.assertEqual(validate_export_manifest(manifest), [])

    def test_preservation_manifest_does_not_mirror_or_capture(self) -> None:
        manifest = build_preservation_manifest({"subject_ref": "candidate.example.v0"})
        self.assertIn("mirror", manifest["blocked_actions"])
        self.assertFalse(manifest["truth_boundary"]["preservation_manifest_mirrors_file"])
        self.assertEqual(validate_preservation_manifest(manifest), [])

    def test_citation_truth_claim_is_rejected(self) -> None:
        bundle = build_citation_bundle({"subject_ref": "candidate.example.v0"})
        bad = copy.deepcopy(bundle)
        bad["truth_boundary"]["citation_bundle_accepts_truth"] = True
        self.assertTrue(any("citation_bundle_accepts_truth" in error for error in validate_citation_bundle(bad)))

    def test_export_public_index_claim_is_rejected(self) -> None:
        manifest = build_export_manifest({"subject_ref": "candidate.example.v0"})
        bad = copy.deepcopy(manifest)
        bad["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(any("public_index_mutated" in error for error in validate_export_manifest(bad)))

    def test_preservation_mirror_claim_is_rejected(self) -> None:
        manifest = build_preservation_manifest({"subject_ref": "candidate.example.v0"})
        bad = copy.deepcopy(manifest)
        bad["truth_boundary"]["preservation_manifest_mirrors_file"] = True
        self.assertTrue(any("preservation_manifest_mirrors_file" in error for error in validate_preservation_manifest(bad)))


if __name__ == "__main__":
    unittest.main()
