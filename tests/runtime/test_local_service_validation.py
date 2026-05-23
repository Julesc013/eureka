from __future__ import annotations

import ast
from pathlib import Path
import unittest

from runtime.local.service import build_request_context, validate_host_allowed
from runtime.local.service.errors import LocalServiceHostError, LocalServiceValidationError


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "runtime" / "local" / "service"
FORBIDDEN_IMPORT_PREFIXES = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
)
FORBIDDEN_VOCABULARY = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE")


class LocalServiceValidationTests(unittest.TestCase):
    def test_query_length_is_limited(self) -> None:
        with self.assertRaises(LocalServiceValidationError):
            build_request_context("GET", "/api/v1/search", "q=" + ("x" * 257), "127.0.0.1")

    def test_non_localhost_client_host_rejected(self) -> None:
        with self.assertRaises(LocalServiceHostError):
            validate_host_allowed("10.0.0.1")

    def test_runtime_package_has_no_forbidden_imports(self) -> None:
        for path in RUNTIME_DIR.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    modules = [node.module or ""]
                for module in modules:
                    self.assertFalse(
                        any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES),
                        f"forbidden import {module} in {path}",
                    )

    def test_runtime_package_has_no_task_or_h_series_vocabulary(self) -> None:
        for path in RUNTIME_DIR.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in FORBIDDEN_VOCABULARY:
                self.assertNotIn(token, text, f"{token} found in {path}")


if __name__ == "__main__":
    unittest.main()
