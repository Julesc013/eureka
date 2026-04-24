from __future__ import annotations

import tempfile
import unittest

from runtime.engine.interfaces.public import (
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
    PlannedSearchRunRequest,
)
from runtime.engine.memory.memory_builder import ResolutionMemoryBuilder
from runtime.engine.memory.tests.test_support import (
    KNOWN_TARGET_REF,
    MISSING_TARGET_REF,
    build_demo_run_service,
)


class ResolutionMemoryBuilderTestCase(unittest.TestCase):
    def test_builds_successful_resolution_memory_from_exact_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run = build_demo_run_service(temp_dir).run_exact_resolution(
                ExactResolutionRunRequest.from_parts(KNOWN_TARGET_REF),
            )
        memory = ResolutionMemoryBuilder().build_from_run(
            memory_id="memory-successful-resolution-0001",
            run=run,
            created_at="2026-04-25T00:00:00+00:00",
        )

        self.assertEqual(memory.memory_kind, "successful_resolution")
        self.assertEqual(memory.source_run_id, run.run_id)
        self.assertTrue(
            isinstance(memory.primary_resolved_resource_id, str)
            and memory.primary_resolved_resource_id.startswith("resolved:")
        )
        self.assertIn("synthetic-fixtures", memory.checked_source_ids)
        self.assertEqual(memory.raw_query, None)

    def test_builds_successful_search_memory_from_search_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run = build_demo_run_service(temp_dir).run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("synthetic"),
            )
        memory = ResolutionMemoryBuilder().build_from_run(
            memory_id="memory-successful-search-0001",
            run=run,
            created_at="2026-04-25T00:00:00+00:00",
        )

        self.assertEqual(memory.memory_kind, "successful_search")
        self.assertEqual(memory.raw_query, "synthetic")
        self.assertGreaterEqual(len(memory.result_summaries), 1)
        self.assertIn("synthetic-fixtures", memory.useful_source_ids)

    def test_builds_absence_memory_from_missing_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run = build_demo_run_service(temp_dir).run_exact_resolution(
                ExactResolutionRunRequest.from_parts(MISSING_TARGET_REF),
            )
        memory = ResolutionMemoryBuilder().build_from_run(
            memory_id="memory-absence-finding-0001",
            run=run,
            created_at="2026-04-25T00:00:00+00:00",
        )

        self.assertEqual(memory.memory_kind, "absence_finding")
        self.assertIsNotNone(memory.absence_report)
        self.assertEqual(memory.result_summaries, ())
        self.assertIsNone(memory.primary_resolved_resource_id)

    def test_preserves_resolution_task_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run = build_demo_run_service(temp_dir).run_planned_search(
                PlannedSearchRunRequest.from_parts("latest Firefox before XP support ended"),
            )
        memory = ResolutionMemoryBuilder().build_from_run(
            memory_id="memory-absence-finding-0002",
            run=run,
            created_at="2026-04-25T00:00:00+00:00",
        )

        self.assertIsNotNone(memory.resolution_task)
        self.assertEqual(memory.task_kind, "find_software_release")
        self.assertEqual(memory.raw_query, "latest Firefox before XP support ended")


if __name__ == "__main__":
    unittest.main()
