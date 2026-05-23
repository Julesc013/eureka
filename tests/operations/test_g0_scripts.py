import json
import subprocess
import sys
import unittest


class G0ScriptTests(unittest.TestCase):
    def run_json(self, *args: str) -> dict:
        completed = subprocess.run([sys.executable, *args], capture_output=True, text=True, check=True)
        return json.loads(completed.stdout)

    def test_score_explain_identity_and_user_cost_scripts(self) -> None:
        fixture = "examples/search/quality/sample_quality_fixture.json"
        self.assertEqual(self.run_json("scripts/eureka_g0_score.py", "--fixture", fixture, "--json")["score_count"], 8)
        self.assertEqual(self.run_json("scripts/eureka_g0_explain.py", "--fixture", fixture, "--json")["explanation_count"], 8)
        self.assertFalse(self.run_json("scripts/eureka_g0_identity.py", "--fixture", fixture, "--json")["accepted_identity_merge_created"])
        self.assertEqual(self.run_json("scripts/eureka_g0_user_cost.py", "--fixture", fixture, "--json")["user_cost_count"], 8)


if __name__ == "__main__":
    unittest.main()
