from __future__ import annotations

import unittest

from surfaces.web.workbench import render_archive_resolution_evals_html


class ArchiveResolutionEvalsRenderingTestCase(unittest.TestCase):
    def test_eval_page_renders_suite_summary(self) -> None:
        html = render_archive_resolution_evals_html(
            {
                "status": "evaluated",
                "eval_suite": {
                    "total_task_count": 1,
                    "status_counts": {"capability_gap": 1},
                    "task_summaries": [
                        {
                            "task_id": "windows_7_apps",
                            "overall_status": "capability_gap",
                            "planner_status": "satisfied",
                            "search_mode": "local_index",
                            "search_observed_result_count": 0,
                        }
                    ],
                    "tasks": [
                        {
                            "task_id": "windows_7_apps",
                            "overall_status": "capability_gap",
                            "planner_status": "satisfied",
                            "search_mode": "local_index",
                            "search_observed_result_count": 0,
                            "capability_gaps": [
                                {
                                    "message": "Current bounded corpus does not contain this artifact.",
                                }
                            ],
                        }
                    ],
                    "created_at": "2026-04-24T00:00:00+00:00",
                    "created_by_slice": "archive_resolution_eval_runner_v0",
                    "load_errors": [],
                    "notices": [],
                },
            },
            requested_task_id="windows_7_apps",
        )

        self.assertIn("Eureka Archive Resolution Evals", html)
        self.assertIn("Suite Summary", html)
        self.assertIn("windows_7_apps", html)
        self.assertIn("capability_gap", html)


if __name__ == "__main__":
    unittest.main()
