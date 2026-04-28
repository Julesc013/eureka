from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN = REPO_ROOT / "tests" / "parity" / "RUST_LOCAL_INDEX_PARITY_PLAN.md"
CASES = REPO_ROOT / "tests" / "parity" / "rust_local_index_cases.json"
SCHEMA = REPO_ROOT / "tests" / "parity" / "local_index_acceptance.schema.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_rust_local_index_parity_plan.py"


class RustLocalIndexParityPlanningTestCase(unittest.TestCase):
    def test_plan_and_case_map_exist(self) -> None:
        self.assertTrue(PLAN.is_file())
        self.assertTrue(CASES.is_file())
        self.assertTrue(SCHEMA.is_file())

        fixture = _load_json(CASES)
        self.assertEqual(fixture["status"], "planning_only")
        self.assertTrue(fixture["python_remains_oracle"])
        self.assertFalse(fixture["rust_local_index_implemented"])
        self.assertFalse(fixture["runtime_wiring_allowed"])

    def test_required_query_cases_are_planned(self) -> None:
        fixture = _load_json(CASES)
        queries = {case["query"] for case in fixture["query_cases"]}
        required = {
            "synthetic",
            "archive",
            "windows 7",
            "firefox xp",
            "registry repair",
            "blue ftp",
            "thinkpad",
            "driver.inf",
            "ray tracing",
            "pc magazine",
            "creative ct1740",
            "3c905",
            "internet-archive-recorded-fixtures",
            "no-such-local-index-hit",
        }

        self.assertLessEqual(required, queries)
        current = [case for case in fixture["query_cases"] if case["golden_status"] == "current"]
        planned = [
            case
            for case in fixture["query_cases"]
            if case["golden_status"] == "planned_future_oracle_extension"
        ]
        self.assertEqual(len(current), 3)
        self.assertGreaterEqual(len(planned), 10)

    def test_required_record_kinds_and_current_status_counts_are_declared(self) -> None:
        fixture = _load_json(CASES)
        record_kinds = set(fixture["required_record_kinds"])
        self.assertEqual(
            record_kinds,
            {
                "source_record",
                "resolved_object",
                "state_or_release",
                "representation",
                "member",
                "synthetic_member",
                "evidence",
            },
        )
        build_case = fixture["build_status_case"]
        self.assertEqual(build_case["expected_record_count"], 489)
        self.assertEqual(build_case["expected_record_kind_counts"]["source_record"], 9)
        self.assertEqual(build_case["expected_record_kind_counts"]["synthetic_member"], 31)

    def test_plan_keeps_python_oracle_and_no_runtime_wiring(self) -> None:
        text = PLAN.read_text(encoding="utf-8").lower()

        for phrase in (
            "python remains the oracle",
            "planning only",
            "rust local index parity implementation is not started",
            "rust remains unwired",
            "no runtime wiring",
            "no rust local-index implementation",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("rust local index parity is implemented", text)

    def test_acceptance_schema_declares_required_report_fields(self) -> None:
        schema = _load_json(SCHEMA)
        required = set(schema["required_top_level_fields"])
        self.assertLessEqual(
            {
                "parity_id",
                "oracle_version",
                "rust_candidate_version",
                "cargo_status",
                "build_status",
                "query_cases",
                "normalized_outputs",
                "divergences",
                "accepted_divergences",
                "failed_cases",
                "notes",
            },
            required,
        )

    def test_no_rust_index_implementation_or_runtime_wiring_exists(self) -> None:
        self.assertFalse((REPO_ROOT / "crates" / "eureka-core" / "src" / "local_index.rs").exists())
        self.assertFalse((REPO_ROOT / "crates" / "eureka-index").exists())

        forbidden = re.compile(
            r"rust_local_index|local_index_parity_candidate|rust_index_candidate|rust_index",
            re.IGNORECASE,
        )
        violations: list[str] = []
        for root in [REPO_ROOT / "runtime", REPO_ROOT / "surfaces"]:
            for path in root.rglob("*.py"):
                if forbidden.search(path.read_text(encoding="utf-8")):
                    violations.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(violations, [])

    def test_crates_do_not_claim_production_local_index(self) -> None:
        forbidden_claims = (
            "rust local index is production",
            "rust local index parity is complete",
            "rust replaces python local index",
        )
        violations: list[str] = []
        for path in (REPO_ROOT / "crates").rglob("*.rs"):
            text = path.read_text(encoding="utf-8").lower()
            for claim in forbidden_claims:
                if claim in text:
                    violations.append(f"{path.relative_to(REPO_ROOT)}: {claim}")
        self.assertEqual(violations, [])

    def test_validator_passes_and_json_parses(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(plain.returncode, 0, plain.stderr)

        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["check_id"], "rust_local_index_parity_planning_v0")
        self.assertTrue(payload["python_remains_oracle"])
        self.assertFalse(payload["rust_local_index_implemented"])
        self.assertFalse(payload["runtime_wiring_allowed"])
        self.assertGreaterEqual(payload["case_count"], 14)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
