from __future__ import annotations

from copy import deepcopy
import io
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from scripts.summarize_observation_candidates import main as summarize_main
from scripts.validate_agent_assisted_observation_policy import (
    AGENT_POLICY_PATH,
    SOURCE_MODES_PATH,
    validate_agent_assisted_observation_policy,
    validate_agent_policy,
    validate_source_access_modes,
)
from scripts.validate_observation_candidate import validate_observation_candidates


REPO_ROOT = Path(__file__).resolve().parents[2]


class AgentAssistedObservationPolicyTest(unittest.TestCase):
    def test_policy_inventory_validates(self) -> None:
        report = validate_agent_assisted_observation_policy(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_source_access_modes_validate(self) -> None:
        modes = _read_json(REPO_ROOT / SOURCE_MODES_PATH)

        self.assertEqual(validate_source_access_modes(modes, SOURCE_MODES_PATH), [])

    def test_missing_forbidden_action_fails(self) -> None:
        policy = _read_json(REPO_ROOT / AGENT_POLICY_PATH)
        broken = deepcopy(policy)
        broken["forbidden_agent_actions"].remove("scrape_google_search_results")

        errors = validate_agent_policy(broken, "broken_policy")

        self.assertTrue(any("scrape_google_search_results" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        policy = _read_json(REPO_ROOT / AGENT_POLICY_PATH)
        broken = deepcopy(policy)
        broken["product_boundary"]["opened_browsers"] = True

        errors = validate_agent_policy(broken, "broken_policy")

        self.assertTrue(any("opened_browsers" in error for error in errors))

    def test_source_mode_current_agent_access_fails(self) -> None:
        modes = _read_json(REPO_ROOT / SOURCE_MODES_PATH)
        broken = deepcopy(modes)
        for mode in broken["modes"]:
            if mode["mode_id"] == "manual_human_only":
                mode["current_agent_access_allowed"] = True

        errors = validate_source_access_modes(broken, "broken_modes")

        self.assertTrue(any("manual_human_only" in error for error in errors))

    def test_summarizer_produces_deterministic_output(self) -> None:
        first = io.StringIO()
        second = io.StringIO()

        self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json"], stdout=first), 0)
        self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json"], stdout=second), 0)

        self.assertEqual(first.getvalue(), second.getvalue())
        payload = json.loads(first.getvalue())
        self.assertEqual(payload["candidate_count"], 4)
        self.assertEqual(payload["by_review_need"], {"review_required": 4})

    def test_summarizer_writes_only_when_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "summary.json"
            result = summarize_main(
                ["--repo-root", str(REPO_ROOT), "--json-output", str(output_path)],
                stdout=io.StringIO(),
            )
            self.assertEqual(result, 0)
            self.assertTrue(output_path.exists())

    def test_validators_do_not_call_network(self) -> None:
        with patch.object(socket, "create_connection", side_effect=AssertionError("network call")) as mocked:
            policy_report = validate_agent_assisted_observation_policy(REPO_ROOT)
            candidate_report = validate_observation_candidates(REPO_ROOT)

        self.assertEqual(policy_report["status"], "valid")
        self.assertEqual(candidate_report["status"], "valid")
        mocked.assert_not_called()

    def test_validators_do_not_mutate_files(self) -> None:
        watched = [
            REPO_ROOT / AGENT_POLICY_PATH,
            REPO_ROOT / SOURCE_MODES_PATH,
            REPO_ROOT / "examples/observation_candidates/minimal_observation_candidate_v0.json",
        ]
        before = _fingerprint(watched)

        validate_agent_assisted_observation_policy(REPO_ROOT)
        validate_observation_candidates(REPO_ROOT)

        self.assertEqual(before, _fingerprint(watched))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fingerprint(paths: list[Path]) -> list[tuple[str, int, int]]:
    return sorted((str(path), path.stat().st_size, path.stat().st_mtime_ns) for path in paths)


if __name__ == "__main__":
    unittest.main()
