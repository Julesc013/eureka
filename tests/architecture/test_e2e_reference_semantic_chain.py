from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs" / "architecture" / "E2E_REFERENCE_SEMANTIC_CHAIN.md"
MAP = ROOT / "docs" / "reference" / "E2E_REFERENCE_CONTRACT_MAP.md"
STATE = ROOT / "docs" / "reference" / "E2E_REFERENCE_STATE_TRANSITIONS.md"
REPLAY = ROOT / "docs" / "reference" / "E2E_REFERENCE_REPLAY_PROFILE.md"

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


class E2EReferenceSemanticChainDocsTest(unittest.TestCase):
    def test_architecture_doc_names_full_chain_in_order(self) -> None:
        text = ARCH.read_text(encoding="utf-8")
        positions = [text.index(concept) for concept in EXPECTED_CONCEPTS]
        self.assertEqual(positions, sorted(positions))

    def test_contract_map_distinguishes_projections_from_authority(self) -> None:
        text = MAP.read_text(encoding="utf-8")
        self.assertIn("public API summary remains a projection", text)
        self.assertIn("public result card is not core authority", text)
        self.assertIn("ReviewItem cannot substitute for `ReviewDecision`", text)
        self.assertIn("A `Candidate` cannot become a `ReviewedRecord`", text)

    def test_state_doc_contains_forbidden_transitions(self) -> None:
        text = STATE.read_text(encoding="utf-8")
        required = [
            "SourceObservation -> ReviewedRecord directly",
            "EvidenceSummary -> ReviewedRecord directly",
            "Candidate -> ReviewedRecord without explicit ReviewDecision and materialization",
            "PreviewRecord -> ReviewedRecord",
            "synthetic object -> production reviewed record",
            "public projection -> master/store authority",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_replay_doc_blocks_provider_calls_and_truth_creation(self) -> None:
        text = REPLAY.read_text(encoding="utf-8")
        self.assertIn("must not perform live provider calls", text)
        self.assertIn("create accepted truth", text)
        self.assertIn("invalid hashes fail closed", text)


if __name__ == "__main__":
    unittest.main()
