from __future__ import annotations

import ast
from pathlib import Path
import unittest

from runtime.local_eval import get_default_local_eval_suites, get_default_query_suite, validate_localhost_base_url


ROOT = Path(__file__).resolve().parents[2]


class LocalEvalSuitesTests(unittest.TestCase):
    def test_default_suites_exist(self) -> None:
        suites = get_default_local_eval_suites()
        self.assertEqual(
            (
                "service_health",
                "json_search",
                "html_workbench",
                "absence",
                "read_only_safety",
                "worker_queue_safety",
                "latency_smoke",
                "local_state_cleanliness",
            ),
            tuple(suite.name for suite in suites),
        )

    def test_default_query_suite_exists(self) -> None:
        queries = get_default_query_suite()
        self.assertIn("sampleproject", queries)
        self.assertIn("definitely-not-present-local-10", queries)
        self.assertTrue(any(len(query) > 256 for query in queries))

    def test_base_url_must_be_localhost(self) -> None:
        self.assertEqual("http://127.0.0.1:8765", validate_localhost_base_url("http://127.0.0.1:8765"))
        with self.assertRaises(Exception):
            validate_localhost_base_url("http://example.com:8765")

    def test_no_forbidden_imports_in_runtime_package(self) -> None:
        forbidden = (
            "runtime.connectors",
            "runtime.local_foundry",
            "runtime.extraction",
            "runtime.search_quality",
            "requests",
            "httpx",
            "aiohttp",
        )
        for path in (ROOT / "runtime" / "local_eval").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    modules = [node.module or ""]
                for module in modules:
                    self.assertFalse(any(module == item or module.startswith(item + ".") for item in forbidden), module)

    def test_no_production_leakage_terms_in_runtime_package(self) -> None:
        forbidden = ("LOCAL-", "BUNDLE", "task", "prompt", "agent")
        for path in (ROOT / "runtime" / "local_eval").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
