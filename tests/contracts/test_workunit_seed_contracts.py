from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.validate_workunit_seed_candidates import (
    CONVERSION_EXAMPLE_PATHS,
    SEED_EXAMPLE_PATHS,
    validate_conversion_contract_payload,
    validate_conversion_payload,
    validate_seed_contract_payload,
    validate_seed_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class WorkUnitSeedContractsTest(unittest.TestCase):
    def test_seed_contract_json_is_valid_and_declares_boundaries(self) -> None:
        payload = _read_json(REPO_ROOT / "contracts/query/workunit_seed.v0.json")

        errors = validate_seed_contract_payload(payload, "seed_contract")

        self.assertEqual(errors, [])
        self.assertFalse(payload["x-workunit-seed-is-executable"])
        self.assertFalse(payload["x-runtime-workunit-created"])
        self.assertFalse(payload["x-evidence-truth-created"])
        self.assertFalse(payload["x-master-index-mutation-allowed"])

    def test_conversion_contract_json_is_valid_and_declares_boundaries(self) -> None:
        payload = _read_json(REPO_ROOT / "contracts/query/workunit_seed_conversion.v0.json")

        errors = validate_conversion_contract_payload(payload, "conversion_contract")

        self.assertEqual(errors, [])
        self.assertFalse(payload["x-workunit-seed-is-executable"])
        self.assertFalse(payload["x-runtime-workunit-created"])
        self.assertFalse(payload["x-evidence-truth-created"])
        self.assertFalse(payload["x-master-index-mutation-allowed"])

    def test_seed_examples_validate(self) -> None:
        for path in SEED_EXAMPLE_PATHS:
            with self.subTest(path=path):
                payload = _read_json(REPO_ROOT / path)
                self.assertEqual(validate_seed_payload(payload, path, REPO_ROOT), [])

    def test_conversion_examples_validate(self) -> None:
        for path in CONVERSION_EXAMPLE_PATHS:
            with self.subTest(path=path):
                payload = _read_json(REPO_ROOT / path)
                self.assertEqual(validate_conversion_payload(payload, path, REPO_ROOT), [])

    def test_seed_execution_and_truth_boundary_flags_fail_when_true(self) -> None:
        for field in ("execution_allowed_now", "accepted_as_runtime_workunit", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
            with self.subTest(field=field):
                seed = _seed()
                seed[field] = True

                errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

                self.assertTrue(any(field in error for error in errors))

    def test_conversion_execution_and_truth_boundary_flags_fail_when_true(self) -> None:
        for field in ("execution_allowed_now", "accepted_as_runtime_workunit", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
            with self.subTest(field=field):
                conversion = _conversion()
                conversion[field] = True

                errors = validate_conversion_payload(conversion, "broken_conversion", REPO_ROOT)

                self.assertTrue(any(field in error for error in errors))


def _seed() -> dict:
    return deepcopy(_read_json(REPO_ROOT / SEED_EXAMPLE_PATHS[0]))


def _conversion() -> dict:
    return deepcopy(_read_json(REPO_ROOT / CONVERSION_EXAMPLE_PATHS[0]))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
