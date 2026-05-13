from __future__ import annotations

import ast
import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import (
    LocalApplianceError,
    open_local_appliance,
    validate_instance_root,
    validate_no_forbidden_runtime_flags,
    validate_runtime_composition,
)


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
RUNTIME_DIR = ROOT / "runtime" / "local_appliance"
FORBIDDEN_IMPORTS = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "subprocess",
    "socket",
)
FORBIDDEN_TEXT = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE")


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class LocalApplianceValidationTests(unittest.TestCase):
    def test_validate_instance_root_rejects_forbidden_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LocalApplianceError):
                validate_instance_root(Path(tmp) / ".local" / "eureka-instance")

    def test_validate_runtime_composition_accepts_initialized_instance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                self.assertIs(validate_runtime_composition(runtime), runtime)
                validate_no_forbidden_runtime_flags(runtime.status())
            finally:
                runtime.close()

    def test_runtime_package_has_no_forbidden_dependencies(self) -> None:
        for path in RUNTIME_DIR.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    modules = [node.module or ""]
                else:
                    continue
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

    def test_runtime_package_does_not_start_server_or_lan(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in RUNTIME_DIR.glob("*.py"))
        self.assertNotIn("HTTPServer", text)
        self.assertNotIn("socketserver", text)
        self.assertNotIn("0.0.0.0", text)


if __name__ == "__main__":
    unittest.main()
