from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
REMEDIATION = ROOT / "control/inventory/local_total_leakage_remediation_result.json"
DIAGNOSIS = ROOT / "control/inventory/local_total_leakage_diagnosis.json"
ALLOWLIST = ROOT / "control/policies/runtime_architecture_leakage_allowlist.json"
POLICY = ROOT / "control/policies/runtime_architecture_leakage_policy.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class LocalTotalLeakageRemediationTests(unittest.TestCase):
    def test_remediation_refuses_policy_weakening(self):
        payload = load_json(REMEDIATION)
        self.assertEqual("local_total_leakage_remediation_result.v0", payload["schema_version"])
        self.assertFalse(payload["policy_weakened"])
        self.assertFalse(payload["runtime_behavior_changed"])
        self.assertEqual(0, payload["new_unallowlisted_production_findings_after"])
        self.assertIn(payload["leakage_gate_status_after"], {"pass", "warn"})

    def test_false_positive_classification_requires_evidence(self):
        diagnosis = load_json(DIAGNOSIS)
        self.assertEqual("local_total_leakage_diagnosis.v0", diagnosis["schema_version"])
        for candidate in diagnosis.get("false_positives", []):
            self.assertIsInstance(candidate, str)
            self.assertGreater(len(candidate.strip()), 20)

    def test_allowlist_entries_are_precise_and_expiring(self):
        payload = load_json(ALLOWLIST)
        entries = payload.get("entries", [])
        self.assertGreater(len(entries), 0)
        for entry in entries[:50]:
            self.assertIn("path", entry)
            self.assertIn("term", entry)
            self.assertIsInstance(entry.get("line"), int)
            self.assertIsInstance(entry.get("column"), int)
            self.assertIn("context_sha256", entry)
            self.assertEqual(64, len(entry["context_sha256"]))
            self.assertNotEqual("never", entry.get("expires_after_task"))
            self.assertIn("reason", entry)

    def test_policy_keeps_runtime_scan_scope(self):
        policy = load_json(POLICY)
        production_paths = set(policy.get("production_paths", []))
        self.assertIn("runtime/**", production_paths)
        self.assertIn("surfaces/**", production_paths)
        ignored_paths = set(policy.get("ignored_paths", []))
        self.assertNotIn("runtime/**", ignored_paths)
        self.assertNotIn("surfaces/**", ignored_paths)


if __name__ == "__main__":
    unittest.main()
