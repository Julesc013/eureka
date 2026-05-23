import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.demo_review_queue_store import run_demo
from scripts.validate_review_queue_store import validate_store


REPO_ROOT = Path(__file__).resolve().parents[2]


class ReviewQueueIntegrationTests(unittest.TestCase):
    def test_demo_runs_without_network(self):
        output = run_demo(":memory:", ":memory:", ":memory:")
        self.assertEqual("pass", output["status"])
        self.assertEqual(1, output["summary"]["review_item_count"])
        self.assertEqual(1, output["summary"]["decision_count"])

    def test_validator_passes(self):
        result = validate_store(REPO_ROOT)
        self.assertIn(result["status"], {"pass", "pass_with_warnings"})
        self.assertEqual(0, result["network_dependencies"])
        self.assertEqual(0, result["h_series_dependencies"])

    def test_no_h_series_module_import_or_connector_dependency(self):
        banned = ("runtime.connectors", "runtime.local_foundry")
        for path in sorted((REPO_ROOT / "runtime/review/queue").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("h1_", text.lower())
            self.assertNotIn("h14", text.lower())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported = [node.module]
                else:
                    imported = []
                for name in imported:
                    self.assertFalse(any(name == item or name.startswith(item + ".") for item in banned))

    def test_cli_demo_writes_explicit_output_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "review-demo.json"
            command = [
                sys.executable,
                "scripts/demo_review_queue_store.py",
                "--output",
                str(output),
                "--json",
            ]
            completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=True)
            self.assertIn('"status": "pass"', completed.stdout)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
