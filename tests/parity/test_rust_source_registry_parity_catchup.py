from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = REPO_ROOT / "tests" / "parity" / "rust_source_registry_cases.json"
GOLDEN_ROOT = REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0"
RUST_SOURCE_REGISTRY = REPO_ROOT / "crates" / "eureka-core" / "src" / "source_registry.rs"
RUST_LIB = REPO_ROOT / "crates" / "eureka-core" / "src" / "lib.rs"
PARITY_SCRIPT = REPO_ROOT / "scripts" / "check_rust_source_registry_parity.py"


class RustSourceRegistryParityCatchupTestCase(unittest.TestCase):
    def test_fixture_map_covers_current_source_registry_shape(self) -> None:
        fixture = _load_json(CASES_PATH)
        cases = {case["case_id"]: case for case in fixture["cases"]}
        required_cases = {
            "sources_list",
            "synthetic_fixtures",
            "github_releases_recorded_fixtures",
            "internet_archive_recorded_fixtures",
            "local_bundle_fixtures",
            "article_scan_recorded_fixtures",
            "internet_archive_placeholder",
            "local_files_placeholder",
            "software_heritage_placeholder",
            "wayback_memento_placeholder",
        }

        self.assertEqual(fixture["expected_source_count"], 9)
        self.assertTrue(fixture["python_remains_oracle"])
        self.assertFalse(fixture["runtime_wiring_allowed"])
        self.assertLessEqual(required_cases, set(cases))
        for case_id, case in cases.items():
            with self.subTest(case_id=case_id):
                golden_path = GOLDEN_ROOT / "source_registry" / case["python_oracle_file"]
                self.assertTrue(golden_path.is_file(), golden_path)
                golden = _load_json(golden_path)
                self.assertEqual(golden["status_code"], case.get("expected_status_code", 200))
                if case["source_id"] is not None:
                    source = golden["body"]["sources"][0]
                    self.assertEqual(golden["body"]["selected_source_id"], case["source_id"])
                    self.assertEqual(source["status"], case["expected_status"])
                    self.assertEqual(source["coverage_depth"], case["expected_coverage_depth"])
                    self.assertEqual(source["connector_mode"], case["expected_connector_mode"])

    def test_rust_candidate_declares_current_source_fields(self) -> None:
        rust = RUST_SOURCE_REGISTRY.read_text(encoding="utf-8")
        lib = RUST_LIB.read_text(encoding="utf-8")

        for required in (
            "pub struct SourceCapabilityRecord",
            "pub struct SourceCoverageRecord",
            "SOURCE_CAPABILITY_FIELDS",
            "COVERAGE_DEPTHS",
            "supports_member_listing",
            "recorded_fixture_backed",
            "coverage_depth",
            "connector_mode",
            "current_source_outputs_match_python_oracle_goldens",
        ):
            self.assertIn(required, rust)
        for source_id in (
            "article-scan-recorded-fixtures",
            "internet-archive-placeholder",
            "local-files-placeholder",
        ):
            self.assertIn(source_id, rust)
        self.assertIn("pub mod source_registry;", lib)

    def test_parity_script_exists_and_reports_cargo_optionally(self) -> None:
        self.assertTrue(PARITY_SCRIPT.is_file())
        text = PARITY_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("--require-cargo", text)
        self.assertIn("skipped_cargo_unavailable", text)
        self.assertIn("runtime_wiring_allowed", text)

    def test_rust_is_not_wired_into_python_runtime_or_surfaces(self) -> None:
        forbidden = re.compile(r"rust_source_registry_parity|eureka_core|eureka-core")
        violations: list[str] = []
        for root in [REPO_ROOT / "runtime", REPO_ROOT / "surfaces"]:
            for path in root.rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                if forbidden.search(text):
                    violations.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(violations, [])

    def test_docs_keep_python_as_oracle_and_rust_unwired(self) -> None:
        docs = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in [
                REPO_ROOT / "tests" / "parity" / "README.md",
                REPO_ROOT / "tests" / "parity" / "PARITY_PLAN.md",
                REPO_ROOT / "docs" / "architecture" / "RUST_BACKEND_LANE.md",
                REPO_ROOT / "docs" / "roadmap" / "RUST_MIGRATION.md",
            ]
        )

        self.assertIn("rust source registry parity catch-up v0", docs)
        self.assertIn("python remains", docs)
        self.assertIn("oracle", docs)
        self.assertIn("not wired", docs)
        self.assertNotIn("rust is the active backend", docs)
        self.assertNotIn("rust replaces python", docs)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
