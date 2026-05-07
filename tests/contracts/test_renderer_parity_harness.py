from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.validate_renderer_parity_harness import (
    DESIGN_PROFILE_MATRIX_PATH,
    MATRIX_PATH,
    POLICY_PATH,
    REPRESENTATION_PROFILES_PATH,
    ROUTE_MATRIX_PATH,
    SEMANTIC_PARITY_POLICY_PATH,
    _design_profile_ids,
    _representation_ids,
    _route_family_ids,
    _semantic_policy_ids,
    validate_check_matrix,
    validate_parity_case,
    validate_renderer_parity_harness,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class RendererParityHarnessContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.representation_ids = _representation_ids(_read_json(REPO_ROOT / REPRESENTATION_PROFILES_PATH))
        self.design_profile_ids = _design_profile_ids(_read_json(REPO_ROOT / DESIGN_PROFILE_MATRIX_PATH))
        self.route_family_ids = _route_family_ids(_read_json(REPO_ROOT / ROUTE_MATRIX_PATH))
        self.semantic_policy_ids = _semantic_policy_ids(_read_json(REPO_ROOT / SEMANTIC_PARITY_POLICY_PATH))
        policy = _read_json(REPO_ROOT / POLICY_PATH)
        self.semantic_categories = set(policy["semantic_category_vocabulary"])

    def test_harness_policy_validates(self) -> None:
        report = validate_renderer_parity_harness(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_check_matrix_validates(self) -> None:
        matrix = _read_json(REPO_ROOT / MATRIX_PATH)

        errors = validate_check_matrix(
            matrix,
            MATRIX_PATH,
            REPO_ROOT,
            self.representation_ids,
            self.design_profile_ids,
            self.route_family_ids,
            self.semantic_policy_ids,
            self.semantic_categories,
        )

        self.assertEqual(errors, [])

    def test_search_page_current_parity_case_validates(self) -> None:
        case = _read_json(REPO_ROOT / "examples/renderer_parity/search_page_parity_case_v0.json")

        errors = validate_parity_case(
            case,
            "search_page_parity_case_v0.json",
            REPO_ROOT,
            self.representation_ids,
            self.design_profile_ids,
            self.route_family_ids,
            self.semantic_policy_ids,
            self.semantic_categories,
        )

        self.assertEqual(errors, [])

    def test_future_placeholder_cases_validate_without_output_files(self) -> None:
        for path in (
            "examples/renderer_parity/object_page_parity_case_future_v0.json",
            "examples/renderer_parity/source_page_parity_case_future_v0.json",
        ):
            case = _read_json(REPO_ROOT / path)
            errors = validate_parity_case(
                case,
                path,
                REPO_ROOT,
                self.representation_ids,
                self.design_profile_ids,
                self.route_family_ids,
                self.semantic_policy_ids,
                self.semantic_categories,
            )
            self.assertEqual(errors, [])

    def test_duplicate_parity_case_id_fails(self) -> None:
        matrix = _read_json(REPO_ROOT / MATRIX_PATH)
        broken = deepcopy(matrix)
        broken["parity_cases"].append(deepcopy(broken["parity_cases"][0]))

        errors = validate_check_matrix(
            broken,
            "broken_matrix",
            REPO_ROOT,
            self.representation_ids,
            self.design_profile_ids,
            self.route_family_ids,
            self.semantic_policy_ids,
            self.semantic_categories,
        )

        self.assertTrue(any("duplicate parity_case_id" in error for error in errors))

    def test_bad_representation_profile_reference_fails(self) -> None:
        case = _read_json(REPO_ROOT / "examples/renderer_parity/search_page_parity_case_v0.json")
        broken = deepcopy(case)
        broken["representation_profile_refs"].append("missing_profile")

        errors = validate_parity_case(
            broken,
            "broken_case",
            REPO_ROOT,
            self.representation_ids,
            self.design_profile_ids,
            self.route_family_ids,
            self.semantic_policy_ids,
            self.semantic_categories,
        )

        self.assertTrue(any("unknown representation profile missing_profile" in error for error in errors))

    def test_bad_design_profile_reference_fails(self) -> None:
        case = _read_json(REPO_ROOT / "examples/renderer_parity/search_page_parity_case_v0.json")
        broken = deepcopy(case)
        broken["design_profile_refs"].append("missing_design_profile")

        errors = validate_parity_case(
            broken,
            "broken_case",
            REPO_ROOT,
            self.representation_ids,
            self.design_profile_ids,
            self.route_family_ids,
            self.semantic_policy_ids,
            self.semantic_categories,
        )

        self.assertTrue(any("unknown design profile missing_design_profile" in error for error in errors))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
