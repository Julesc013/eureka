import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "e2e_reference_system" / "e2e_reference_contract_v0"
INDEX = AUDIT / "reference_contract_index.json"
EXAMPLE = ROOT / "contracts" / "examples" / "e2e_reference_v0" / "e2e_reference_chain.example.json"

EXPECTED_CONCEPTS = [
    "QueryIntent",
    "ResolutionRun",
    "WorkUnit",
    "SourceObservation",
    "EvidenceSummary",
    "Candidate",
    "PreviewRecord",
    "ReviewItem",
    "ReviewDecision",
    "ReviewedRecord",
    "IndexDelta",
    "SnapshotManifest",
]

TIMESTAMP_FIELDS = {"created_at", "observed_at", "decided_at", "generated_at", "occurred_at"}


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _canonical_hash(identity: dict) -> str:
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _contract_paths(index: dict) -> list[Path]:
    paths: list[Path] = []
    for concept in index["concepts"]:
        for key in ("canonical_contract_path",):
            value = concept[key]
            if value.endswith((".json", ".yaml", ".md")):
                paths.append(ROOT / value)
        for key in ("supporting_contract_paths", "projection_paths"):
            for value in concept.get(key, []):
                paths.append(ROOT / value)
    return sorted(set(paths))


class E2EReferenceContractsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.index = _load_json(INDEX)
        self.example = _load_json(EXAMPLE)

    def test_reference_index_covers_expected_concepts(self) -> None:
        concepts = [entry["concept"] for entry in self.index["concepts"]]
        self.assertEqual(concepts, EXPECTED_CONCEPTS)
        for entry in self.index["concepts"]:
            self.assertIn(entry["owning_plane"], {"Discovery", "Evidence", "Preview", "Truth", "Distribution"})
            self.assertTrue(entry["canonical_contract_path"])
            self.assertTrue(entry["authority_class"])
            self.assertTrue(entry["gap_status"])

    def test_reference_index_paths_exist(self) -> None:
        missing = [str(path.relative_to(ROOT)) for path in _contract_paths(self.index) if not path.exists()]
        self.assertEqual(missing, [])

    def test_selected_json_contract_ids_are_unique(self) -> None:
        ids: dict[str, str] = {}
        duplicates: list[str] = []
        for path in _contract_paths(self.index):
            if path.suffix != ".json":
                continue
            data = _load_json(path)
            contract_id = data.get("$id")
            if not contract_id:
                continue
            if contract_id in ids:
                duplicates.append(f"{contract_id}: {ids[contract_id]} and {path.relative_to(ROOT)}")
            ids[contract_id] = str(path.relative_to(ROOT))
        self.assertEqual(duplicates, [])

    def test_audit_json_files_parse(self) -> None:
        for path in AUDIT.glob("*.json"):
            with self.subTest(path=path.name):
                data = _load_json(path)
                self.assertIn("schema_version", data)

    def test_synthetic_chain_has_all_objects_and_resolved_refs(self) -> None:
        objects = {item["object_id"]: item for item in self.example["objects"]}
        self.assertEqual([item["semantic_type"] for item in self.example["objects"]], EXPECTED_CONCEPTS)
        for item in self.example["objects"]:
            self.assertIn("synthetic", item["object_id"])
            self.assertTrue(item["semantic_identity"]["authority_level"].startswith("synthetic"))
            for value in item.get("refs", {}).values():
                refs = value if isinstance(value, list) else [value]
                for ref in refs:
                    self.assertIn(ref, objects)

    def test_synthetic_hashes_are_stable_and_ignore_timestamps(self) -> None:
        for item in self.example["objects"]:
            self.assertEqual(item["semantic_hash"], _canonical_hash(item["semantic_identity"]))
            mutated = dict(item)
            for field in TIMESTAMP_FIELDS:
                if field in mutated:
                    mutated[field] = "2099-01-01T00:00:00Z"
            self.assertEqual(item["semantic_hash"], _canonical_hash(mutated["semantic_identity"]))

    def test_public_projection_excludes_private_or_secret_material(self) -> None:
        serialized = json.dumps(self.example, sort_keys=True).lower()
        forbidden = ["c:\\", "d:\\", "sk-", "private_key", "credential", "public_eligible\": true"]
        for token in forbidden:
            self.assertNotIn(token, serialized)
        self.assertFalse(self.example["public_eligible"])
        self.assertFalse(self.example["accepted_truth_created"])
        self.assertFalse(self.example["reviewed_master_mutation"])
        self.assertFalse(self.example["public_index_mutation"])

    def test_review_and_materialization_boundaries_are_explicit(self) -> None:
        matrix = _load_json(AUDIT / "state_transition_matrix.json")
        forbidden = set(matrix["forbidden_transitions"])
        self.assertIn("Candidate -> ReviewedRecord without explicit ReviewDecision and materialization", forbidden)
        self.assertIn("ReviewItem", matrix["state_machines"])
        self.assertIn("ReviewDecision", matrix["state_machines"])
        review_item = next(item for item in self.example["objects"] if item["semantic_type"] == "ReviewItem")
        review_decision = next(item for item in self.example["objects"] if item["semantic_type"] == "ReviewDecision")
        self.assertEqual(review_item["status"], "pending")
        self.assertEqual(review_decision["semantic_identity"]["decision"], "promote")
        self.assertTrue(review_decision["local_only_confirmed"])

    def test_replay_profile_unknown_events_and_hashes_are_fail_closed(self) -> None:
        replay = _load_json(AUDIT / "replay_serialization_profile.json")
        self.assertEqual(replay["unknown_event_type_posture"], "preserve_as_inert_unsupported_event")
        self.assertEqual(replay["invalid_hash_posture"], "fail_closed")
        self.assertFalse(replay["provider_calls_during_replay"])
        self.assertFalse(replay["accepted_truth_created_by_replay"])

    def test_versioning_policy_requires_new_version_for_breaking_changes(self) -> None:
        versioning = _load_json(AUDIT / "versioning_and_compatibility.json")
        self.assertFalse(versioning["breaking_v0_changes_allowed_in_place"])
        self.assertTrue(versioning["breaking_change_requires_new_version"])
        self.assertFalse(versioning["store_migrations_in_this_task"])

    def test_control_audit_schema_not_core_product_authority(self) -> None:
        for entry in self.index["concepts"]:
            self.assertFalse(
                entry["canonical_contract_path"].startswith("control/"),
                f"{entry['concept']} uses control path as canonical authority",
            )


if __name__ == "__main__":
    unittest.main()
