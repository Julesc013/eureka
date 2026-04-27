from __future__ import annotations

import unittest

from runtime.gateway import build_demo_archive_resolution_evals_public_api
from runtime.gateway.public_api import ArchiveResolutionEvalRunRequest


class ArchiveResolutionEvalsPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_archive_resolution_evals_public_api()

    def test_run_suite_returns_structured_envelope(self) -> None:
        response = self.public_api.run_suite()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "evaluated")
        self.assertEqual(response.body["eval_suite"]["total_task_count"], 6)
        self.assertEqual(response.body["eval_suite"]["status_counts"], {"satisfied": 6})

    def test_run_one_task_returns_one_task(self) -> None:
        response = self.public_api.run_task(
            ArchiveResolutionEvalRunRequest.from_parts(task_id="windows_7_apps"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["eval_suite"]["total_task_count"], 1)
        self.assertEqual(response.body["eval_suite"]["tasks"][0]["task_id"], "windows_7_apps")


if __name__ == "__main__":
    unittest.main()
