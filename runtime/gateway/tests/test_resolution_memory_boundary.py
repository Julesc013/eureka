from __future__ import annotations

import tempfile
import unittest

from runtime.engine.interfaces.public import (
    DeterministicSearchRunRequest,
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
)
from runtime.engine.memory import (
    LocalResolutionMemoryService,
    LocalResolutionMemoryStore,
    ResolutionMemoryBuilder,
)
from runtime.engine.memory.tests.test_support import build_demo_run_service
from runtime.gateway.public_api.resolution_memory_boundary import ResolutionMemoryPublicApi


class ResolutionMemoryPublicApiTestCase(unittest.TestCase):
    def test_create_read_and_list_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_service = build_demo_run_service(temp_dir)
            run = run_service.run_deterministic_search(
                DeterministicSearchRunRequest.from_parts("synthetic"),
            )
            public_api = self._build_public_api(temp_dir, run_service)

            created = public_api.create_memory_from_run(
                ResolutionMemoryCreateRequest.from_parts(run.run_id),
            )
            read = public_api.get_memory(
                ResolutionMemoryReadRequest.from_parts(created.body["selected_memory_id"]),
            )
            listed = public_api.list_memories(
                ResolutionMemoryCatalogRequest.from_parts(memory_kind="successful_search"),
            )

        self.assertEqual(created.status_code, 200)
        self.assertEqual(read.status_code, 200)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.body["memory_count"], 1)

    def test_unknown_memory_returns_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = self._build_public_api(temp_dir, run_service=None)
            response = public_api.get_memory(
                ResolutionMemoryReadRequest.from_parts("memory-missing-0001"),
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["notices"][0]["code"], "resolution_memory_not_found")

    def _build_public_api(self, root: str, run_service) -> ResolutionMemoryPublicApi:
        return ResolutionMemoryPublicApi(
            LocalResolutionMemoryService(
                memory_store=LocalResolutionMemoryStore(root),
                memory_builder=ResolutionMemoryBuilder(),
                run_service=run_service,
                timestamp_factory=lambda: "2026-04-25T00:00:00+00:00",
            )
        )


if __name__ == "__main__":
    unittest.main()
