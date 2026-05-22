from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CLEANLINESS_SCRIPT = ROOT / "scripts" / "check_generated_artifact_cleanliness.py"
POLICY = ROOT / "control/policies/generated_artifact_policy.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SiteDistNoMutationTests(unittest.TestCase):
    def test_site_dist_mutation_by_ordinary_test_is_detected(self) -> None:
        module = load_module(CLEANLINESS_SCRIPT, "check_generated_artifact_cleanliness")
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual("deployment_generated", module.classify_path("site/dist/index.html", policy))

    def test_public_index_is_canonical_generated(self) -> None:
        module = load_module(CLEANLINESS_SCRIPT, "check_generated_artifact_cleanliness")
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual("canonical_generated", module.classify_path("site/dist/data/public_index/search_documents.ndjson", policy))

    def test_audit_generated_output_is_not_site_dist(self) -> None:
        module = load_module(CLEANLINESS_SCRIPT, "check_generated_artifact_cleanliness")
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        artifact_class = module.classify_path(
            "control/audits/r0-remediation-generated-artifact-drift-01-v0/generated/sample.json",
            policy,
        )
        self.assertEqual("audit_generated", artifact_class)


if __name__ == "__main__":
    unittest.main()
