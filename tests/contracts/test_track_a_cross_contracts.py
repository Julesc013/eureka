from __future__ import annotations

from pathlib import Path
import unittest

from scripts.validate_track_a_contracts import validate_track_a_contracts


REPO_ROOT = Path(__file__).resolve().parents[2]


class TrackACrossContractsTest(unittest.TestCase):
    def test_cross_contract_validator_succeeds_on_current_repo_state(self) -> None:
        report = validate_track_a_contracts(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["validator_count"], 12)

    def test_cross_contract_validator_fails_when_constituent_validator_fails(self) -> None:
        def broken_validator(_root: Path) -> dict:
            return {
                "schema_version": "0.1.0",
                "status": "invalid",
                "errors": ["deliberately broken fixture"],
                "warnings": [],
            }

        report = validate_track_a_contracts(
            REPO_ROOT,
            validators=(("broken_group", "Broken group", broken_validator),),
        )

        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("deliberately broken fixture" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
