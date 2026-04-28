"""Rust migration skeleton structure tests."""

from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CRATES_ROOT = REPO_ROOT / "crates"
EXPECTED_CRATES = (
    "eureka-core",
    "eureka-contracts",
    "eureka-store",
    "eureka-resolver",
)
PLACEHOLDER_CRATES = (
    "eureka-contracts",
    "eureka-store",
    "eureka-resolver",
)


class RustMigrationSkeletonTestCase(unittest.TestCase):
    def test_workspace_and_expected_crates_exist(self) -> None:
        self.assertTrue((CRATES_ROOT / "Cargo.toml").exists())
        self.assertTrue((CRATES_ROOT / "README.md").exists())

        workspace = (CRATES_ROOT / "Cargo.toml").read_text(encoding="utf-8")
        self.assertIn("[workspace]", workspace)
        self.assertIn('resolver = "2"', workspace)

        for crate_name in EXPECTED_CRATES:
            with self.subTest(crate=crate_name):
                crate_root = CRATES_ROOT / crate_name
                self.assertTrue((crate_root / "Cargo.toml").exists())
                self.assertTrue((crate_root / "src" / "lib.rs").exists())
                self.assertIn(crate_name, workspace)

    def test_crates_forbid_unsafe_and_non_candidate_crates_are_placeholders(self) -> None:
        for crate_name in EXPECTED_CRATES:
            with self.subTest(crate=crate_name):
                lib_rs = (CRATES_ROOT / crate_name / "src" / "lib.rs").read_text(
                    encoding="utf-8"
                )
                self.assertIn("#![forbid(unsafe_code)]", lib_rs)
        for crate_name in PLACEHOLDER_CRATES:
            with self.subTest(crate=crate_name):
                lib_rs = (CRATES_ROOT / crate_name / "src" / "lib.rs").read_text(
                    encoding="utf-8"
                )
                self.assertIn("placeholder_only_python_oracle_active", lib_rs)

    def test_eureka_core_declares_isolated_parity_candidates_only(self) -> None:
        lib_rs = (CRATES_ROOT / "eureka-core" / "src" / "lib.rs").read_text(
            encoding="utf-8"
        )
        cargo_toml = (CRATES_ROOT / "eureka-core" / "Cargo.toml").read_text(
            encoding="utf-8"
        )
        source_registry = (
            CRATES_ROOT / "eureka-core" / "src" / "source_registry.rs"
        ).read_text(encoding="utf-8")
        query_planner = (
            CRATES_ROOT / "eureka-core" / "src" / "query_planner.rs"
        ).read_text(encoding="utf-8")

        self.assertIn("pub mod source_registry;", lib_rs)
        self.assertIn("pub mod query_planner;", lib_rs)
        self.assertIn(
            "source_registry_and_query_planner_parity_candidates_v0_python_oracle_active",
            lib_rs,
        )
        self.assertIn("serde", cargo_toml)
        self.assertIn("serde_json", cargo_toml)
        self.assertNotIn("tokio", cargo_toml)
        self.assertNotIn("reqwest", cargo_toml)
        self.assertIn("load_source_registry", source_registry)
        self.assertIn("list_sources_response", source_registry)
        self.assertIn("pub fn plan_query", query_planner)
        self.assertIn("query_planner_candidate_matches_python_oracle_goldens", query_planner)

    def test_docs_record_python_oracle_and_parity_rules(self) -> None:
        docs = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (
                REPO_ROOT / "docs" / "roadmap" / "RUST_MIGRATION.md",
                REPO_ROOT / "docs" / "architecture" / "RUST_BACKEND_LANE.md",
                REPO_ROOT / "tests" / "parity" / "PARITY_PLAN.md",
            )
        )

        self.assertIn("python remains the executable specification", docs)
        self.assertIn("python is the oracle", docs)
        self.assertIn("no big-bang rewrite", docs)
        self.assertIn("parity tests must pass before replacement", docs)
        self.assertIn("python runtime", docs)
        self.assertIn("not wired into runtime", docs)

    def test_docs_keep_rust_and_native_work_deferred(self) -> None:
        rust_lane = (
            REPO_ROOT / "docs" / "architecture" / "RUST_BACKEND_LANE.md"
        ).read_text(encoding="utf-8").lower()
        native_later = (
            REPO_ROOT / "docs" / "roadmap" / "NATIVE_APPS_LATER.md"
        ).read_text(encoding="utf-8").lower()

        self.assertIn("no rust gateway, cli, ffi, service, worker", rust_lane)
        self.assertIn("no native app work is started", rust_lane)
        self.assertIn("native app work is intentionally deferred", native_later)
        self.assertIn("rust skeleton does not change that policy", native_later)


if __name__ == "__main__":
    unittest.main()
