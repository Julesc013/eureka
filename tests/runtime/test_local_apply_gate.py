from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.local.apply import APPLY_CONFIRMATION, ROLLBACK_CONFIRMATION, run_local_apply
from scripts.eureka_init_instance import initialize_instance


def make_instance() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tmp = tempfile.TemporaryDirectory(prefix="eureka-local-apply-test-")
    instance = Path(tmp.name) / "instance"
    result = initialize_instance(instance)
    if result["status"] not in {"pass", "pass_with_warnings"}:
        tmp.cleanup()
        raise AssertionError(result)
    return tmp, instance


class LocalApplyGateTests(unittest.TestCase):
    def test_dry_run_does_not_mutate(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)
        before = (instance / "db" / "public_index.sqlite").read_bytes()

        result = run_local_apply(target_instance=instance)

        self.assertEqual(result["status"], "dry_run")
        self.assertTrue(result["dry_run_preview_passed"])
        self.assertFalse(result["apply_performed"])
        self.assertEqual(before, (instance / "db" / "public_index.sqlite").read_bytes())

    def test_apply_requires_token(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)

        result = run_local_apply(target_instance=instance, apply=True, confirmation=APPLY_CONFIRMATION)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("operator token is required for apply", result["blocked_reasons"])

    def test_apply_requires_confirmation(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)

        result = run_local_apply(target_instance=instance, apply=True, operator_token="local-dev-token")

        self.assertEqual(result["status"], "blocked")
        self.assertIn(f"confirmation must be {APPLY_CONFIRMATION}", result["blocked_reasons"])

    def test_repo_path_target_is_blocked(self) -> None:
        result = run_local_apply(
            target_instance=Path.cwd(),
            apply=True,
            operator_token="local-dev-token",
            confirmation=APPLY_CONFIRMATION,
        )

        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("repo" in reason.lower() for reason in result["blocked_reasons"]))


if __name__ == "__main__":
    unittest.main()
