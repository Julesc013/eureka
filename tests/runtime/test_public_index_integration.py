import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.demo_reviewed_public_index import run_demo
from scripts.validate_reviewed_public_index import validate


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicIndexIntegrationTests(unittest.TestCase):
    def test_demo_runs_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = run_demo(root / "source.sqlite", root / "evidence.sqlite", root / "review.sqlite", root / "public.sqlite")
            self.assertEqual("pass", output["status"])
            self.assertEqual(1, output["public_index_summary"]["record_count"])
            self.assertFalse(output["site_dist_mutated"])
            self.assertFalse(output["master_index_mutated"])

    def test_validator_passes(self):
        result = validate()
        self.assertEqual("pass", result["status"])
        self.assertEqual(0, result["network_dependencies"])
        self.assertEqual(0, result["h_series_dependencies"])
        self.assertTrue(result["f0_should_remain_blocked"])
        self.assertTrue(result["dev_to_main_should_remain_blocked"])

    def test_no_h_series_module_import_or_connector_dependency(self):
        banned = ("runtime.connectors", "runtime.local_foundry", "runtime.search_quality")
        for path in sorted((REPO_ROOT / "runtime/public_index").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("h1_", text)
            self.assertNotIn("h14", text)
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
            root = Path(tmp)
            output = root / "public-demo.json"
            command = [
                sys.executable,
                "scripts/demo_reviewed_public_index.py",
                "--source-cache-db",
                str(root / "source.sqlite"),
                "--evidence-db",
                str(root / "evidence.sqlite"),
                "--review-db",
                str(root / "review.sqlite"),
                "--public-index-db",
                str(root / "public.sqlite"),
                "--output",
                str(output),
                "--json",
            ]
            completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=True)
            self.assertIn('"status": "pass"', completed.stdout)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
