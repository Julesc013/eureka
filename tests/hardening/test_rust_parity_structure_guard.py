import re
import unittest

from tests.hardening.helpers import iter_text_files, load_json, repo_path, read_text


class RustParityStructureGuardTest(unittest.TestCase):
    def test_rust_workspace_and_source_registry_candidate_exist(self):
        expected = [
            "crates/Cargo.toml",
            "crates/eureka-core/Cargo.toml",
            "crates/eureka-core/src/lib.rs",
            "crates/eureka-core/src/source_registry.rs",
            "crates/eureka-core/src/query_planner.rs",
            "crates/eureka-contracts/Cargo.toml",
            "crates/eureka-store/Cargo.toml",
            "crates/eureka-resolver/Cargo.toml",
            "tests/parity/rust_query_planner_cases.json",
        ]
        missing = [path for path in expected if not repo_path(path).exists()]
        self.assertEqual(missing, [])
        source_registry = read_text("crates/eureka-core/src/source_registry.rs")
        query_planner = read_text("crates/eureka-core/src/query_planner.rs")
        self.assertIn("list_output_matches_python_oracle_golden", source_registry)
        self.assertIn("#[cfg(test)]", source_registry)
        self.assertIn("query_planner_candidate_matches_python_oracle_goldens", query_planner)
        self.assertIn("#[cfg(test)]", query_planner)

    def test_python_runtime_and_surfaces_do_not_import_rust_candidate(self):
        forbidden = re.compile(r"eureka_core|source_registry_parity|crates[\\/]eureka-core")
        violations = []
        for path in iter_text_files(["runtime", "surfaces", "scripts"]):
            if path.suffix != ".py":
                continue
            text = path.read_text(encoding="utf-8")
            if forbidden.search(text):
                violations.append(str(path.relative_to(repo_path("."))))
        self.assertEqual(violations, [])

    def test_docs_keep_python_oracle_and_no_production_rust_claims(self):
        docs = [
            "docs/architecture/RUST_BACKEND_LANE.md",
            "docs/roadmap/RUST_MIGRATION.md",
            "tests/parity/README.md",
            "tests/parity/PARITY_PLAN.md",
        ]
        text = "\n".join(read_text(path).lower() for path in docs)
        self.assertIn("python remains", text)
        self.assertIn("oracle", text)
        self.assertIn("not wired", text)

        forbidden_claims = [
            "rust is the active backend",
            "rust replaces python",
            "rust production backend is implemented",
            "rust backend is production-ready",
        ]
        for claim in forbidden_claims:
            self.assertNotIn(claim, text)

    def test_cargo_commands_remain_optional(self):
        registry = load_json("control/inventory/tests/test_registry.json")
        records = {record["test_id"]: record for record in registry["records"]}
        matrix = load_json("control/inventory/tests/command_matrix.json")
        lanes = {lane["lane_id"]: lane for lane in matrix["lanes"]}

        self.assertEqual(lanes["rust_optional"]["required_status"], "optional")
        self.assertEqual(records["cargo_check_optional"]["advisory_or_required"], "optional")
        self.assertEqual(records["cargo_test_optional"]["advisory_or_required"], "optional")
        self.assertEqual(
            records["rust_query_planner_parity_check"]["advisory_or_required"],
            "required",
        )

    def test_allowed_divergence_placeholder_exists_without_accepted_records(self):
        path = repo_path("tests/parity/ALLOWED_DIVERGENCES.md")
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").lower()
        self.assertIn("no accepted divergences", text)
        self.assertFalse(repo_path("tests/parity/allowed_divergences.json").exists())


if __name__ == "__main__":
    unittest.main()
