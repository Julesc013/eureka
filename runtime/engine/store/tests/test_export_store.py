from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.engine.interfaces.public.resolution import ObjectSummary
from runtime.engine.store import LocalExportStore, artifact_id_for_bytes


class LocalExportStoreTestCase(unittest.TestCase):
    def test_artifact_identity_is_deterministic_for_same_bytes(self) -> None:
        payload = b'{"manifest_kind":"eureka.resolution_manifest"}\n'

        first = artifact_id_for_bytes(payload)
        second = artifact_id_for_bytes(payload)

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("sha256:"))

    def test_store_artifact_persists_metadata_bytes_and_target_index(self) -> None:
        payload = b'{"manifest_kind":"eureka.resolution_manifest"}\n'
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalExportStore(temp_dir)

            metadata = store.store_artifact(
                artifact_kind="resolution_manifest",
                target_ref="fixture:software/synthetic-demo-app@1.0.0",
                content_type="application/json; charset=utf-8",
                payload=payload,
                source_action="store_resolution_manifest",
                filename="eureka-resolution-manifest-fixture-software-synthetic-demo-app-1.0.0.json",
                primary_object=ObjectSummary(
                    id="obj.synthetic-demo-app",
                    kind="software",
                    label="Synthetic Demo App",
                ),
            )

            self.assertEqual(metadata.artifact_id, artifact_id_for_bytes(payload))
            self.assertEqual(store.get_artifact_bytes(metadata.artifact_id), payload)
            self.assertEqual(
                store.list_artifacts_for_target("fixture:software/synthetic-demo-app@1.0.0"),
                (metadata,),
            )

            object_path = Path(temp_dir) / Path(metadata.store_path)
            self.assertTrue(object_path.exists())

            metadata_path = Path(temp_dir) / "metadata" / f"{metadata.artifact_id.replace(':', '--')}.json"
            self.assertTrue(metadata_path.exists())
            metadata_payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata_payload["artifact_id"], metadata.artifact_id)
            self.assertEqual(metadata_payload["primary_object"]["id"], "obj.synthetic-demo-app")

    def test_store_reuses_the_same_artifact_identity_for_same_payload(self) -> None:
        payload = b"synthetic bundle payload"
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalExportStore(temp_dir)

            first = store.store_artifact(
                artifact_kind="resolution_bundle",
                target_ref="fixture:software/synthetic-demo-app@1.0.0",
                content_type="application/zip",
                payload=payload,
                source_action="store_resolution_bundle",
                filename="eureka-resolution-bundle.zip",
            )
            second = store.store_artifact(
                artifact_kind="resolution_bundle",
                target_ref="fixture:software/synthetic-demo-app@1.0.0",
                content_type="application/zip",
                payload=payload,
                source_action="store_resolution_bundle",
                filename="eureka-resolution-bundle.zip",
            )

            self.assertEqual(first.artifact_id, second.artifact_id)
            artifacts = store.list_artifacts_for_target("fixture:software/synthetic-demo-app@1.0.0")
            self.assertEqual(len(artifacts), 1)

