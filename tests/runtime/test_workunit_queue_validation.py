from __future__ import annotations

import ast
from pathlib import Path
import unittest

from runtime.worker.workunit_queue import (
    ALLOWED_WORKUNIT_STATES,
    ALLOWED_WORKUNIT_TYPES,
    WorkUnit,
    WorkUnitValidationError,
    validate_workunit,
    validate_workunit_kind,
    validate_workunit_state,
)


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_DIR = ROOT / "runtime" / "worker" / "workunit_queue"
FORBIDDEN_IMPORTS = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
)
FORBIDDEN_TEXT = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE")


class WorkUnitQueueValidationTests(unittest.TestCase):
    def test_workunit_validates_required_fields(self) -> None:
        validate_workunit(WorkUnit.new("search_need", "Valid"))
        with self.assertRaises(WorkUnitValidationError):
            validate_workunit(WorkUnit.new("search_need", ""))

    def test_required_types_and_states_are_supported(self) -> None:
        self.assertIn("agent_task", ALLOWED_WORKUNIT_TYPES)
        for kind in ALLOWED_WORKUNIT_TYPES:
            self.assertEqual(kind, validate_workunit_kind(kind).value)
        for state in ALLOWED_WORKUNIT_STATES:
            self.assertEqual(state, validate_workunit_state(state).value)

    def test_runtime_package_has_no_forbidden_imports(self) -> None:
        for path in RUNTIME_DIR.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    modules = [node.module or ""]
                for module in modules:
                    self.assertFalse(
                        any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORTS),
                        f"{path} imports {module}",
                    )

    def test_runtime_package_has_no_task_or_h_series_vocabulary(self) -> None:
        for path in RUNTIME_DIR.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in FORBIDDEN_TEXT:
                self.assertNotIn(token, text, f"{token} found in {path}")


if __name__ == "__main__":
    unittest.main()
