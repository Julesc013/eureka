from __future__ import annotations

import ast
from pathlib import Path
import unittest

from runtime.local_worker import BLOCKED_WORKER_KINDS, ENABLED_WORKER_KINDS, get_default_worker_registry


ROOT = Path(__file__).resolve().parents[2]


class LocalWorkerRegistryTests(unittest.TestCase):
    def test_registry_lists_enabled_and_blocked_workers(self) -> None:
        registry = get_default_worker_registry()
        self.assertEqual(
            (
                "noop_worker",
                "review_queue_checker",
                "reviewed_index_rebuild_worker",
                "absence_report_worker",
                "local_status_snapshot_worker",
            ),
            tuple(ENABLED_WORKER_KINDS),
        )
        self.assertEqual(
            (
                "source_probe_worker",
                "extraction_worker",
                "agent_research_worker",
                "ai_model_worker",
                "download_worker",
                "install_execute_worker",
                "source_sync_worker",
                "lan_worker",
                "deployment_worker",
            ),
            tuple(BLOCKED_WORKER_KINDS),
        )
        self.assertEqual(tuple(ENABLED_WORKER_KINDS), registry.enabled_kinds())
        self.assertEqual(tuple(BLOCKED_WORKER_KINDS), registry.blocked_kinds())

    def test_disabled_workers_are_not_executable(self) -> None:
        registry = get_default_worker_registry()
        for kind in ("source_probe_worker", "extraction_worker", "ai_model_worker"):
            worker = registry.get_worker(kind)
            self.assertIsNotNone(worker)
            self.assertFalse(worker.enabled)
            self.assertIsNone(worker.run)

    def test_no_forbidden_imports_in_runtime_package(self) -> None:
        forbidden = (
            "runtime.connectors",
            "runtime.local_foundry",
            "runtime.extraction",
            "runtime.search_quality",
            "requests",
            "httpx",
            "aiohttp",
            "urllib.request",
        )
        for path in (ROOT / "runtime" / "local_worker").glob("*.py"):
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
        for path in (ROOT / "runtime" / "local_worker").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
