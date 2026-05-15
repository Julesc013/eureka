from __future__ import annotations

import unittest

from runtime.local_eval import build_json_report, build_markdown_summary, validate_eval_report, validate_no_forbidden_eval_effects


class LocalEvalReportsTests(unittest.TestCase):
    def test_json_report_validates(self) -> None:
        report = build_json_report(
            "http://127.0.0.1:8765",
            [
                {
                    "suite": "service_health",
                    "status": "pass",
                    "case_count": 1,
                    "passed_case_count": 1,
                    "failed_case_count": 0,
                    "cases": [{"case_id": "status", "passed": True, "elapsed_ms": 1.0}],
                }
            ],
        )
        self.assertEqual("pass", report["status"])
        validate_no_forbidden_eval_effects(validate_eval_report(report))

    def test_markdown_summary_generation(self) -> None:
        report = build_json_report("http://127.0.0.1:8765", [])
        summary = build_markdown_summary(report)
        self.assertIn("Local Eval Summary", summary)
        self.assertIn("external_network_used: false", summary)


if __name__ == "__main__":
    unittest.main()
