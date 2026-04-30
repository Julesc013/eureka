from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
SNAPSHOT_ROOT = REPO_ROOT / "snapshots" / "examples" / "static_snapshot_v0"
PUBLIC_SITE = REPO_ROOT / "site/dist"

REQUIRED_SNAPSHOT_FILES = {
    "README_FIRST.txt",
    "index.html",
    "index.txt",
    "SNAPSHOT_MANIFEST.json",
    "BUILD_MANIFEST.json",
    "SOURCE_SUMMARY.json",
    "EVAL_SUMMARY.json",
    "ROUTE_SUMMARY.json",
    "PAGE_REGISTRY.json",
    "CHECKSUMS.SHA256",
    "SIGNATURES.README.txt",
    "data/README.txt",
}
FORBIDDEN_SUFFIXES = {
    ".exe",
    ".dll",
    ".msi",
    ".dmg",
    ".pkg",
    ".pem",
    ".key",
    ".pfx",
    ".p12",
    ".env",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class SignedSnapshotFormatTest(unittest.TestCase):
    def test_snapshot_contract_and_docs_exist(self) -> None:
        contract = load_json(PUBLICATION_DIR / "snapshot_contract.json")

        self.assertEqual(contract["snapshot_contract_id"], "eureka-static-snapshot-format")
        self.assertEqual(contract["snapshot_format_version"], "0.1.0")
        self.assertFalse(contract["production_signed_release"])
        self.assertFalse(contract["real_signing_keys_present"])
        self.assertFalse(contract["contains_real_binaries"])

        for doc in (
            "docs/reference/SNAPSHOT_FORMAT_CONTRACT.md",
            "docs/reference/SNAPSHOT_SIGNATURE_POLICY.md",
        ):
            with self.subTest(doc=doc):
                text = (REPO_ROOT / doc).read_text(encoding="utf-8").casefold()
                self.assertIn("no real signing keys", text)
                self.assertIn("no executable", text)
                self.assertIn("not a production", text)

    def test_seed_snapshot_contains_required_static_files(self) -> None:
        actual = {
            str(path.relative_to(SNAPSHOT_ROOT)).replace("\\", "/")
            for path in SNAPSHOT_ROOT.rglob("*")
            if path.is_file()
        }

        self.assertTrue(REQUIRED_SNAPSHOT_FILES.issubset(actual))
        for relative in REQUIRED_SNAPSHOT_FILES:
            with self.subTest(relative=relative):
                self.assertTrue((SNAPSHOT_ROOT / relative).is_file())

    def test_seed_snapshot_is_not_signed_release_or_binary_mirror(self) -> None:
        for path in SNAPSHOT_ROOT.rglob("*"):
            if not path.is_file():
                continue
            with self.subTest(path=path):
                self.assertFalse({suffix.lower() for suffix in path.suffixes} & FORBIDDEN_SUFFIXES)
                text = path.read_text(encoding="utf-8")
                lowered = text.casefold()
                self.assertNotIn("production ready", lowered)
                self.assertNotIn("backend deployed", lowered)
                self.assertNotIn("live probes enabled", lowered)
                self.assertNotIn("real private keys are included", lowered)

        signature_text = (SNAPSHOT_ROOT / "SIGNATURES.README.txt").read_text(encoding="utf-8").casefold()
        self.assertIn("no production signing is performed", signature_text)
        self.assertIn("no private keys are stored", signature_text)
        self.assertIn("not full authenticity proof", signature_text)

    def test_snapshot_manifests_keep_static_only_flags(self) -> None:
        for name in ("SNAPSHOT_MANIFEST.json", "BUILD_MANIFEST.json"):
            with self.subTest(name=name):
                payload = load_json(SNAPSHOT_ROOT / name)
                self.assertEqual(payload["snapshot_format_version"], "0.1.0")
                self.assertFalse(payload["production_signed_release"])
                self.assertFalse(payload["real_signing_keys_present"])
                self.assertFalse(payload["contains_real_binaries"])
                self.assertFalse(payload["contains_live_backend"])
                self.assertFalse(payload["contains_live_probes"])
                self.assertFalse(payload["contains_external_observations"])

    def test_publication_inventory_marks_snapshot_route_future(self) -> None:
        capabilities = load_json(PUBLICATION_DIR / "surface_capabilities.json")
        by_id = {item["id"]: item for item in capabilities["capabilities"]}
        snapshots = by_id["snapshots"]

        self.assertIn(snapshots["status"], {"planned", "deferred"})
        self.assertFalse(snapshots["enabled_by_default"])
        self.assertIn("snapshots/examples/static_snapshot_v0/", snapshots["implemented_paths"])
        self.assertIn("/snapshots/", snapshots["reserved_paths"])

        matrix = load_json(PUBLICATION_DIR / "surface_route_matrix.json")
        route = {item["id"]: item for item in matrix["surfaces"]}["snapshots"]
        self.assertFalse(route["implemented_now"])
        self.assertIn("snapshots/examples/static_snapshot_v0/", route["implemented_paths"])

    def test_files_surface_references_snapshot_limitations(self) -> None:
        manifest = load_json(PUBLIC_SITE / "files" / "manifest.json")

        self.assertEqual(manifest["snapshot_seed_example"], "snapshots/examples/static_snapshot_v0")
        self.assertFalse(manifest["production_signed_snapshots_available"])
        self.assertFalse(manifest["real_signing_keys_present"])

        for relative in ("files/index.html", "files/index.txt", "files/README.txt"):
            text = (PUBLIC_SITE / relative).read_text(encoding="utf-8").casefold()
            with self.subTest(relative=relative):
                self.assertIn("signed snapshot format v0", text)
                self.assertIn("production signed", text)
                self.assertTrue("not available" in text or "no production signed" in text)
                self.assertIn("no executable", text)


if __name__ == "__main__":
    unittest.main()
