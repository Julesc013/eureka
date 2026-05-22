from __future__ import annotations

import ast
import hashlib
import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_service import LocalServiceApp
from surfaces.web.workbench.local_html.errors import LocalWorkbenchValidationError
from surfaces.web.workbench.local_html.validation import (
    validate_local_workbench_page,
    validate_no_external_assets,
    validate_no_forbidden_claims,
    validate_no_mutation_controls,
    validate_no_mutation_controls as validate_controls,
)
from runtime.public_index import PublicIndexStore
from tests.runtime.test_public_index_store import make_record


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
)


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class LocalWorkbenchReadOnlyTests(unittest.TestCase):
    def test_validation_rejects_mutating_or_external_html(self) -> None:
        with self.assertRaises(LocalWorkbenchValidationError):
            validate_local_workbench_page('<html lang="en"><head><title>x</title></head><body><nav></nav><main><form method="post"></form></main></body></html>')
        with self.assertRaises(LocalWorkbenchValidationError):
            validate_no_mutation_controls("<button>create WorkUnit</button>")
        with self.assertRaises(LocalWorkbenchValidationError):
            validate_no_external_assets('<link href="https://example.invalid/style.css">')
        with self.assertRaises(LocalWorkbenchValidationError):
            validate_no_forbidden_claims("production ready")

    def test_html_routes_preserve_json_api_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            with PublicIndexStore.open(instance / "db" / "public_index.sqlite") as store:
                store.write_record(make_record())
            runtime = open_local_appliance(instance, read_only=True)
            try:
                app = LocalServiceApp(runtime)
                html = app.handle("GET", "/search", "q=demo")
                json_response = app.handle("GET", "/api/v1/search", "q=demo")
                json_via_format = app.handle("GET", "/search", "q=demo&format=json")
                self.assertEqual("text/html; charset=utf-8", html.content_type)
                self.assertEqual("application/json; charset=utf-8", json_response.content_type)
                self.assertEqual("application/json; charset=utf-8", json_via_format.content_type)
                self.assertEqual(1, json_response.payload["result_count"])
            finally:
                close_local_appliance(runtime)

    def test_html_requests_do_not_mutate_instance_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            before = tree_digest(instance)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                app = LocalServiceApp(runtime)
                for path in ("/", "/status", "/search?q=demo", "/absence?q=missing", "/object/not-present", "/source/not-present"):
                    response = app.handle("GET", path)
                    self.assertLess(response.status_code, 500)
            finally:
                close_local_appliance(runtime)
            self.assertEqual(before, tree_digest(instance))

    def test_write_methods_remain_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                app = LocalServiceApp(runtime)
                for method in ("POST", "PUT", "PATCH", "DELETE"):
                    self.assertEqual(405, app.handle(method, "/search", "q=demo").status_code)
            finally:
                close_local_appliance(runtime)

    def test_workbench_imports_stay_inside_allowed_boundary(self) -> None:
        for path in (ROOT / "runtime" / "local_workbench").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    modules = [node.module or ""]
                for module in modules:
                    self.assertFalse(any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES))


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name.endswith("-journal") or path.name.endswith("-wal") or path.name.endswith("-shm"):
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
