from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock
import unittest

from scripts.evaluate_node_policy import main as evaluate_node_policy_main
from scripts.validate_node_policy_evaluator import validate


ROOT = Path(__file__).resolve().parents[2]
SAFE_ARGS = [
    "--node-manifest",
    "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
    "--node-policy",
    "examples/nodes/policies/local_private_node_policy_v0.json",
    "--workunit",
    "examples/work_units/search_need_review_v0/work_unit.json",
]


class NodePolicyEvaluatorScriptTests(unittest.TestCase):
    def test_evaluator_writes_no_files_by_default(self) -> None:
        before = _tracked_relevant_files()
        stdout = io.StringIO()

        result = evaluate_node_policy_main([*SAFE_ARGS, "--check"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertIn("Decision: allowed_for_dry_run", stdout.getvalue())
        self.assertEqual(before, _tracked_relevant_files())

    def test_evaluator_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "node_policy_evaluation_result.json"
            summary = Path(tmp) / "node_policy_evaluation_summary.md"
            stdout = io.StringIO()
            result = evaluate_node_policy_main(
                [*SAFE_ARGS, "--output", str(output), "--summary-output", str(summary), "--json"],
                stdout=stdout,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertEqual(payload["schema_version"], "node_policy_evaluation_result.v0")
        self.assertEqual(payload["decision"], "allowed_for_dry_run")
        self.assertIn("Node Policy Evaluation", summary_text)

    def test_evaluator_refuses_site_dist_output(self) -> None:
        forbidden = ROOT / "site" / "dist" / "__node_policy_eval_forbidden.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [sys.executable, "scripts/evaluate_node_policy.py", *SAFE_ARGS, "--output", str(forbidden)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_evaluator_refuses_runtime_output_for_reports(self) -> None:
        forbidden = ROOT / "runtime" / "__node_policy_eval_forbidden.json"
        if forbidden.exists():
            forbidden.unlink()

        completed = subprocess.run(
            [sys.executable, "scripts/evaluate_node_policy.py", *SAFE_ARGS, "--output", str(forbidden)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(forbidden.exists())

    def test_evaluator_lists_examples(self) -> None:
        stdout = io.StringIO()

        result = evaluate_node_policy_main(["--list-examples"], stdout=stdout)

        self.assertEqual(result, 0)
        self.assertIn("local_private_allowed", stdout.getvalue())

    def test_validator_passes_current_repo(self) -> None:
        errors = validate()

        self.assertEqual(errors, [])

    def test_runtime_script_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            stdout = io.StringIO()
            result = evaluate_node_policy_main([*SAFE_ARGS, "--check", "--json"], stdout=stdout)

        payload = json.loads(stdout.getvalue())
        self.assertEqual(result, 0)
        self.assertFalse(payload["product_boundary"]["enabled_network_access"])
        self.assertFalse(payload["product_boundary"]["enabled_model_provider_calls"])

    def test_validator_does_not_create_local_private_roots(self) -> None:
        before = _private_root_state()

        errors = validate()

        self.assertEqual(errors, [])
        self.assertEqual(before, _private_root_state())


def _tracked_relevant_files() -> list[str]:
    roots = [
        ROOT / "control" / "audits" / "track-b-11-node-policy-evaluator-v0" / "generated",
        ROOT / "examples" / "node_policy_evaluations",
    ]
    results: list[str] = []
    for root in roots:
        if root.exists():
            results.extend(path.relative_to(ROOT).as_posix() for path in root.rglob("*") if path.is_file())
    return sorted(results)


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (ROOT / ".aide.local").exists(),
        ".local/eureka": (ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (ROOT / ".cache" / "eureka").exists(),
    }


if __name__ == "__main__":
    unittest.main()

