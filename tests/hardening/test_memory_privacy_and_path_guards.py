import json
import unittest

from surfaces.web.server.server_config import WebServerConfig
from tests.hardening.helpers import find_private_path_leaks, load_json, repo_path, read_text


FORBIDDEN_MEMORY_KEYS = {
    "account_id",
    "index_path",
    "local_path",
    "memory_store_root",
    "private_path",
    "run_store_root",
    "store_root",
    "user_id",
}


def _iter_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _iter_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_keys(item)


class MemoryPrivacyAndPathGuardsTest(unittest.TestCase):
    def test_resolution_memory_docs_keep_local_manual_non_cloud_scope(self):
        docs = "\n".join(
            [
                read_text("runtime/engine/memory/README.md"),
                read_text("docs/architecture/RESOLUTION_MEMORY.md"),
            ]
        ).lower()
        self.assertIn("local", docs)
        self.assertIn("manual", docs)
        self.assertTrue("no shared or cloud memory" in docs or "not cloud/shared memory" in docs)
        self.assertIn("private local paths", docs)
        self.assertIn("stay private by default", docs)

    def test_resolution_memory_goldens_do_not_store_private_roots(self):
        root = repo_path("tests/parity/golden/python_oracle/v0/resolution_memory")
        leaks = []
        forbidden_key_hits = []
        for path in sorted(root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            leaks.extend(
                f"{path.relative_to(repo_path('.'))}: {leak}"
                for leak in find_private_path_leaks(payload)
            )
            forbidden_key_hits.extend(
                f"{path.relative_to(repo_path('.'))}: {key}"
                for key in _iter_keys(payload)
                if key in FORBIDDEN_MEMORY_KEYS
            )

        self.assertEqual(leaks, [])
        self.assertEqual(forbidden_key_hits, [])

    def test_public_alpha_status_with_memory_root_does_not_leak_path(self):
        sentinel = r"D:\private\eureka-memory-root"
        status = WebServerConfig.public_alpha(memory_store_root=sentinel).to_status_dict()
        serialized = json.dumps(status, sort_keys=True)

        self.assertNotIn(sentinel, serialized)
        self.assertEqual(status["configured_root_kinds"]["memory_store_root"], "configured")
        self.assertEqual(find_private_path_leaks(status), [])

    def test_memory_related_goldens_and_audit_json_have_no_private_paths(self):
        paths = [
            "tests/parity/golden/python_oracle/v0/resolution_memory",
            "control/audits/2026-04-25-comprehensive-test-eval-audit",
        ]
        leaks = []
        for root in paths:
            for path in sorted(repo_path(root).rglob("*.json")):
                payload = load_json(path.relative_to(repo_path(".")))
                leaks.extend(
                    f"{path.relative_to(repo_path('.'))}: {leak}"
                    for leak in find_private_path_leaks(payload)
                )
        self.assertEqual(leaks, [])


if __name__ == "__main__":
    unittest.main()
