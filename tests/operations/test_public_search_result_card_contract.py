from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CARD_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_result_card.v0.json"
RESPONSE_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_response.v0.json"
EXAMPLES_DIR = REPO_ROOT / "contracts" / "api" / "examples"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md"
AUDIT_PACK = REPO_ROOT / "control" / "audits" / "public-search-result-card-contract-v0"


REQUIRED_LANES = {
    "best_direct_answer",
    "installable_or_usable_now",
    "inside_bundles",
    "official",
    "preservation",
    "community",
    "documentation",
    "mentions_or_traces",
    "absence_or_next_steps",
    "still_searching",
    "other",
}
UNSAFE_ACTIONS = {
    "download",
    "install_handoff",
    "execute",
    "upload",
}


class PublicSearchResultCardContractTest(unittest.TestCase):
    def test_schema_and_examples_parse(self) -> None:
        self.assertTrue(CARD_SCHEMA.is_file())
        self.assertIsInstance(json.loads(CARD_SCHEMA.read_text(encoding="utf-8")), dict)
        examples = sorted(EXAMPLES_DIR.glob("search_result_card_*.v0.json"))
        self.assertGreaterEqual(len(examples), 5)
        for path in examples:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["contract_id"], "eureka_public_search_result_card_v0")

    def test_required_stable_fields_and_lanes_present(self) -> None:
        payload = json.loads(CARD_SCHEMA.read_text(encoding="utf-8"))
        required = set(payload["required"])
        for field in (
            "result_id",
            "title",
            "record_kind",
            "result_lane",
            "user_cost",
            "source",
            "identity",
            "evidence",
            "compatibility",
            "actions",
            "rights",
            "risk",
            "warnings",
            "limitations",
            "gaps",
        ):
            self.assertIn(field, required)
        lanes = set(payload["properties"]["result_lane"]["enum"])
        self.assertTrue(REQUIRED_LANES.issubset(lanes))

    def test_actions_distinguish_allowed_blocked_and_future_gated(self) -> None:
        payload = json.loads(CARD_SCHEMA.read_text(encoding="utf-8"))
        actions = payload["$defs"]["actions"]
        self.assertEqual(set(actions["required"]), {"allowed", "blocked", "future_gated"})
        statuses = set(payload["$defs"]["action_entry"]["properties"]["status"]["enum"])
        self.assertTrue({"allowed", "blocked", "future_gated", "unavailable"}.issubset(statuses))
        blocked_or_future = set(payload["x-blocked_or_future_gated_actions"])
        self.assertTrue(UNSAFE_ACTIONS.issubset(blocked_or_future))
        self.assertTrue(UNSAFE_ACTIONS.isdisjoint(set(payload["x-default_allowed_actions"])))

    def test_examples_do_not_allow_unsafe_actions(self) -> None:
        demonstrated = set()
        for path in EXAMPLES_DIR.glob("search_result_card_*.v0.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            allowed = {entry["action_id"] for entry in payload["actions"]["allowed"]}
            blocked = {entry["action_id"] for entry in payload["actions"]["blocked"]}
            future = {entry["action_id"] for entry in payload["actions"]["future_gated"]}
            with self.subTest(path=path.name):
                self.assertTrue(UNSAFE_ACTIONS.isdisjoint(allowed))
            demonstrated.update((blocked | future) & UNSAFE_ACTIONS)
        self.assertTrue(UNSAFE_ACTIONS.issubset(demonstrated))

    def test_rights_and_risk_do_not_claim_clearance_or_safety(self) -> None:
        schema = json.loads(CARD_SCHEMA.read_text(encoding="utf-8"))
        rights = schema["$defs"]["rights"]["properties"]
        risk = schema["$defs"]["risk"]["properties"]
        self.assertNotIn("cleared", rights["rights_status"]["enum"])
        self.assertIn("unknown", rights["distribution_allowed"]["enum"])
        self.assertNotIn("clean", risk["malware_scan_status"]["enum"])
        self.assertIn("not_scanned", risk["malware_scan_status"]["enum"])

    def test_search_response_aligns_with_card_contract(self) -> None:
        payload = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(payload["x-result_card_schema"], "contracts/api/search_result_card.v0.json")
        self.assertTrue(payload["x-results_are_public_search_result_cards"])
        result_props = payload["$defs"]["result"]["properties"]
        for field in ("source", "identity", "rights", "risk", "warnings", "gaps"):
            self.assertIn(field, result_props)

    def test_audit_pack_and_docs_state_boundaries(self) -> None:
        self.assertTrue((AUDIT_PACK / "RESULT_CARD_FIELD_MATRIX.md").is_file())
        self.assertTrue((AUDIT_PACK / "public_search_result_card_contract_report.json").is_file())
        text = REFERENCE_DOC.read_text(encoding="utf-8").casefold()
        for phrase in (
            "contract-only",
            "local public search runtime v0",
            "local/prototype result",
            "hosted public exposure still waits",
            "does not enable downloads",
            "installers",
            "execution",
            "not a production ranking guarantee",
            "must not claim malware safety",
            "must not claim rights clearance",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        for claim in (
            "/api/v1/search is live",
            "result cards are emitted by a live hosted backend",
            "production api stability is guaranteed",
        ):
            with self.subTest(claim=claim):
                self.assertNotIn(claim, text)


if __name__ == "__main__":
    unittest.main()
