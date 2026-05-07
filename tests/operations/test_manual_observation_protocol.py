from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from scripts.validate_manual_observation_protocol import (
    ANTI_FABRICATION_RULES,
    FAILURE_CLASSES,
    POLICY_PATH,
    TAXONOMY_PATH,
    VALID_EXAMPLE_PATHS,
    INVALID_EXAMPLE_PATH,
    validate_manual_observation_protocol,
    validate_observation_example,
    validate_pending_batch,
    validate_policy,
    validate_required_docs,
    validate_taxonomy,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class ManualObservationProtocolTest(unittest.TestCase):
    def test_validator_passes_current_repo(self) -> None:
        report = validate_manual_observation_protocol(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_missing_protocol_doc_fails(self) -> None:
        errors = validate_required_docs(REPO_ROOT, ["docs/operations/DOES_NOT_EXIST.md"], "docs")

        self.assertTrue(any("missing" in error for error in errors))

    def test_missing_anti_fabrication_rule_fails(self) -> None:
        policy = _read_json(REPO_ROOT / POLICY_PATH)
        broken = deepcopy(policy)
        broken["anti_fabrication_rules"].remove("no_invented_titles")

        errors = validate_policy(broken, "broken_policy")

        self.assertTrue(any("no_invented_titles" in error for error in errors))

    def test_missing_failure_taxonomy_class_fails(self) -> None:
        taxonomy = _read_json(REPO_ROOT / TAXONOMY_PATH)
        broken = deepcopy(taxonomy)
        broken["classes"] = [item for item in broken["classes"] if item["class_id"] != "source_gap"]

        errors, class_ids = validate_taxonomy(broken, "broken_taxonomy")

        self.assertNotIn("source_gap", class_ids)
        self.assertTrue(any("source_gap" in error for error in errors))

    def test_valid_observed_result_example_passes(self) -> None:
        taxonomy_classes = _taxonomy_classes()
        example = _read_json(REPO_ROOT / "examples/manual_observations/valid_observed_result_v0.json")

        errors = validate_observation_example(example, "valid_observed_result", taxonomy_classes=taxonomy_classes)

        self.assertEqual(errors, [])

    def test_valid_no_result_example_passes(self) -> None:
        taxonomy_classes = _taxonomy_classes()
        example = _read_json(REPO_ROOT / "examples/manual_observations/valid_no_result_observation_v0.json")

        errors = validate_observation_example(example, "valid_no_result", taxonomy_classes=taxonomy_classes)

        self.assertEqual(errors, [])

    def test_invalid_fabricated_example_fails(self) -> None:
        taxonomy_classes = _taxonomy_classes()
        example = _read_json(REPO_ROOT / INVALID_EXAMPLE_PATH)

        errors = validate_observation_example(example, INVALID_EXAMPLE_PATH, taxonomy_classes=taxonomy_classes)

        self.assertTrue(errors)
        self.assertTrue(any("fabricated_results" in error or "manual_session_completed" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        policy = _read_json(REPO_ROOT / POLICY_PATH)
        broken = deepcopy(policy)
        broken["product_boundary"]["opened_browsers"] = True

        errors = validate_policy(broken, "broken_policy")

        self.assertTrue(any("opened_browsers" in error for error in errors))

    def test_pending_slot_marked_observed_without_observation_fields_fails(self) -> None:
        payload = {
            "observation_status": "pending_manual_observation",
            "observations": [
                {
                    "observation_id": "slot",
                    "observation_status": "observed",
                    "observed_at": None,
                    "top_results": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pending.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            errors = validate_pending_batch(path, Path(temp))

        self.assertTrue(any("marked observed" in error for error in errors))

    def test_validator_does_not_call_network(self) -> None:
        with patch.object(socket, "create_connection", side_effect=AssertionError("network call")) as mocked:
            report = validate_manual_observation_protocol(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        mocked.assert_not_called()

    def test_validator_does_not_mutate_files(self) -> None:
        paths = [REPO_ROOT / POLICY_PATH, REPO_ROOT / TAXONOMY_PATH]
        paths.extend(REPO_ROOT / path for path in VALID_EXAMPLE_PATHS)
        before = _fingerprint(paths)

        validate_manual_observation_protocol(REPO_ROOT)

        self.assertEqual(before, _fingerprint(paths))

    def test_policy_lists_required_rule_sets(self) -> None:
        policy = _read_json(REPO_ROOT / POLICY_PATH)

        self.assertTrue(ANTI_FABRICATION_RULES.issubset(set(policy["anti_fabrication_rules"])))
        self.assertEqual(len(FAILURE_CLASSES), 17)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _taxonomy_classes() -> set[str]:
    taxonomy = _read_json(REPO_ROOT / TAXONOMY_PATH)
    return {item["class_id"] for item in taxonomy["classes"]}


def _fingerprint(paths: list[Path]) -> list[tuple[str, int, int]]:
    return sorted((str(path), path.stat().st_size, path.stat().st_mtime_ns) for path in paths)


if __name__ == "__main__":
    unittest.main()
