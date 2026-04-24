from __future__ import annotations

import tempfile
import unittest

from runtime.engine.interfaces.public import (
    DeterministicSearchRunRequest,
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
)
from runtime.engine.interfaces.service import (
    ResolutionMemoryNotFoundError,
    ResolutionMemorySourceRunNotFoundError,
)
from runtime.engine.memory import (
    LocalResolutionMemoryService,
    LocalResolutionMemoryStore,
    ResolutionMemoryBuilder,
)
from runtime.engine.memory.tests.test_support import build_demo_run_service


class LocalResolutionMemoryServiceTestCase(unittest.TestCase):
    def test_creates_memory_from_existing_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_service = build_demo_run_service(temp_dir)
            run = run_service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("synthetic"),
            )
            service = self._build_service(temp_dir, run_service=run_service)
            memory = service.create_memory_from_run(
                ResolutionMemoryCreateRequest.from_parts(run.run_id),
            )

        self.assertEqual(memory.source_run_id, run.run_id)
        self.assertEqual(memory.memory_kind, "successful_search")
        self.assertGreaterEqual(len(memory.result_summaries), 1)

    def test_lists_and_reads_memories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_service = build_demo_run_service(temp_dir)
            run = run_service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("synthetic"),
            )
            service = self._build_service(temp_dir, run_service=run_service)
            created = service.create_memory_from_run(
                ResolutionMemoryCreateRequest.from_parts(run.run_id),
            )
            loaded = service.get_memory(ResolutionMemoryReadRequest.from_parts(created.memory_id))
            listed = service.list_memories(
                ResolutionMemoryCatalogRequest.from_parts(memory_kind="successful_search"),
            )

        self.assertEqual(loaded.memory_id, created.memory_id)
        self.assertEqual([memory.memory_id for memory in listed], [created.memory_id])

    def test_unknown_memory_raises_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(temp_dir, run_service=None)
            with self.assertRaises(ResolutionMemoryNotFoundError):
                service.get_memory(ResolutionMemoryReadRequest.from_parts("memory-missing-0001"))

    def test_unknown_run_raises_source_run_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_service = build_demo_run_service(temp_dir)
            service = self._build_service(temp_dir, run_service=run_service)
            with self.assertRaises(ResolutionMemorySourceRunNotFoundError):
                service.create_memory_from_run(
                    ResolutionMemoryCreateRequest.from_parts("run-missing-0001"),
                )

    def _build_service(
        self,
        root: str,
        *,
        run_service,
    ) -> LocalResolutionMemoryService:
        return LocalResolutionMemoryService(
            memory_store=LocalResolutionMemoryStore(root),
            memory_builder=ResolutionMemoryBuilder(),
            run_service=run_service,
            timestamp_factory=lambda: "2026-04-25T00:00:00+00:00",
        )


if __name__ == "__main__":
    unittest.main()
