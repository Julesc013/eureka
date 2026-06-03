from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class TemporalSemanticInterfaceContractsTest(unittest.TestCase):
    def test_view_contract_stubs_are_tsis_contracts(self) -> None:
        view_paths = [
            "contracts/view/search_page/search_page.v0.json",
            "contracts/view/result_card/result_card.v0.json",
            "contracts/view/object_page/object_page.v0.json",
            "contracts/view/need_page/need_page.v0.json",
            "contracts/view/candidate_page/candidate_page.v0.json",
            "contracts/view/source_page/source_page.v0.json",
            "contracts/view/evidence_page/evidence_page.v0.json",
            "contracts/view/status_page/status_page.v0.json",
        ]

        for relative in view_paths:
            payload = _read_json(relative)
            self.assertTrue(payload["x-tsis_contract"], relative)
            self.assertIn("semantic_entities", payload["required"], relative)
            self.assertIn("result_states", payload["required"], relative)

    def test_registries_use_stable_machine_vocabulary(self) -> None:
        status_registry = _read_json("control/inventory/semantic_status_registry.json")
        affordance_registry = _read_json("control/inventory/semantic_affordance_registry.json")
        representation_registry = _read_json("control/inventory/representation_profile_registry.json")

        self.assertFalse(status_registry["machine_status_synonyms_allowed"])
        self.assertFalse(status_registry["color_only_status_allowed"])
        self.assertFalse(affordance_registry["renderer_policy_decision_allowed"])
        self.assertTrue(representation_registry["unknown_profile_fallback_required"])
        self.assertFalse(representation_registry["profile_selection_may_change_route_identity"])


def _read_json(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
