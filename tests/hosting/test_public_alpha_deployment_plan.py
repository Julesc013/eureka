
import json
import unittest
from pathlib import Path

from scripts.check_public_alpha_deployment_plan import check_plan
from scripts.validate_public_alpha_deployment_plan import validate_public_alpha_deployment_plan

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = REPO_ROOT / "examples/hosting/deployment"


class PublicAlphaDeploymentPlanTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((EXAMPLE_ROOT / name).read_text(encoding="utf-8"))

    def test_validator_passes_current_repo(self) -> None:
        report = validate_public_alpha_deployment_plan(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_deployment_plan_validates(self) -> None:
        plan = self.load("public_alpha_deployment_plan_v0.json")
        self.assertEqual(check_plan(plan), [])
        self.assertEqual(plan["plan_status"], "planning_only")

    def test_deployment_step_contract_shape_is_embedded(self) -> None:
        plan = self.load("public_alpha_deployment_plan_v0.json")
        step = plan["deployment_steps"][0]
        self.assertEqual(step["schema_version"], "public_alpha_deployment_step.v0")
        self.assertFalse(step["external_provider_action"])

    def test_environment_matrix_validates(self) -> None:
        matrix = self.load("public_alpha_environment_matrix_v0.json")
        self.assertEqual(len(matrix["environments"]), 6)
        self.assertTrue(all(env["launch_allowed_current"] is False for env in matrix["environments"]))

    def test_static_backend_split_validates(self) -> None:
        split = self.load("public_alpha_static_backend_split_v0.json")
        self.assertFalse(split["static_site_role"]["can_run_python_backend"])
        self.assertFalse(split["hosted_backend_role"]["public_backend_started"])

    def test_provider_neutral_profile_validates(self) -> None:
        profile = self.load("public_alpha_provider_profile_provider_neutral_v0.json")
        self.assertTrue(profile["provider_neutral"])
        self.assertFalse(profile["credentials_required_current"])


if __name__ == "__main__":
    unittest.main()
