from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "docs" / "operations" / "FUTURE_TASK_COMPLETION_STANDARD.md"
HANDOFF = ROOT / "docs" / "operations" / "R0_TO_F0_HANDOFF.md"


class R0FutureTaskGateTests(unittest.TestCase):
    def test_future_task_standard_rejects_scaffold_only_completion(self):
        text = STANDARD.read_text(encoding="utf-8")
        self.assertIn("A task is not complete merely because contracts, policies, examples, validators, or audit reports exist.", text)
        self.assertIn("runtime code", text)
        self.assertIn("tests", text)
        self.assertIn("explicit command output", text)
        self.assertIn("persistent state where applicable", text)
        self.assertIn("audit evidence", text)
        self.assertIn("no forbidden side effects", text)

    def test_future_task_standard_requires_warning_disposition(self):
        text = STANDARD.read_text(encoding="utf-8")
        self.assertIn("PASS_WITH_WARNINGS may advance only if every warning is:", text)
        self.assertIn("child-tasked", text)
        self.assertIn("explicitly blocking", text)

    def test_f0_handoff_requires_recovered_seams(self):
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("F0 may proceed only by using recovered runtime seams.", text)
        self.assertIn("F0 must not recreate H-series scaffold-only patterns.", text)
        self.assertIn("F0 must not create task-named runtime packages.", text)
        self.assertIn("F0 must persist observations/evidence/review/index data through R0 seams where applicable.", text)
        self.assertIn("F0 must prove behavior before expanding.", text)


if __name__ == "__main__":
    unittest.main()
