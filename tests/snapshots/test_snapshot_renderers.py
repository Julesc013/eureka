import unittest

from runtime.snapshots.manifest import build_snapshot_manifest
from runtime.snapshots.render_file_tree import render_snapshot_file_tree_index
from runtime.snapshots.render_lite_html import render_snapshot_lite_html
from runtime.snapshots.render_text import render_snapshot_text


class SnapshotRendererTests(unittest.TestCase):
    def setUp(self):
        self.manifest = build_snapshot_manifest(
            [
                {
                    "record_type": "search_result",
                    "canonical_ref": "fixture:search:renderer",
                    "title": "Renderer Result",
                    "summary": "Renderer fixture.",
                    "blocked_actions": ["download", "execute"],
                }
            ]
        )
        self.bundle = {"manifest": self.manifest}

    def test_text_renderer_preserves_required_semantic_fields(self):
        result = render_snapshot_text(self.bundle)
        self.assertTrue(result["required_semantic_fields_present"])
        self.assertIn("Source posture", result["content"])
        self.assertFalse(result["product_boundary"]["enabled_hosting"])

    def test_lite_html_renderer_preserves_required_semantic_fields(self):
        result = render_snapshot_lite_html(self.bundle)
        self.assertTrue(result["required_semantic_fields_present"])
        self.assertIn("Rights posture", result["content"])
        self.assertFalse(result["product_boundary"]["enabled_relay"])

    def test_file_tree_renderer_preserves_required_semantic_fields(self):
        result = render_snapshot_file_tree_index(self.bundle)
        content = result["content"].casefold()
        for phrase in ("identity", "source posture", "evidence posture", "rights posture", "risk posture", "action posture", "limitations"):
            self.assertIn(phrase, content)
        self.assertFalse(result["truth_boundary"]["snapshot_executes_actions"])


if __name__ == "__main__":
    unittest.main()
