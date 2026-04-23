from __future__ import annotations

import unittest

from runtime.gateway.public_api import compatibility_envelope_to_view_model


class CompatibilityViewModelsTestCase(unittest.TestCase):
    def test_compatibility_envelope_maps_to_shared_view_model_shape(self) -> None:
        view_model = compatibility_envelope_to_view_model(
            {
                "status": "evaluated",
                "target_ref": "fixture:software/compatibility-lab@3.2.1",
                "host_profile": {
                    "host_profile_id": "windows-x86_64",
                    "os_family": "windows",
                    "architecture": "x86_64",
                    "features": [],
                },
                "compatibility_status": "compatible",
                "resolved_resource_id": "resolved:sha256:test",
                "primary_object": {
                    "id": "obj.compatibility-lab",
                    "kind": "software",
                    "label": "Compatibility Lab",
                },
                "source": {
                    "family": "synthetic_fixture",
                    "label": "Synthetic Fixture",
                    "locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                },
                "reasons": [
                    {
                        "code": "os_family_supported",
                        "message": "Host os_family 'windows' matches the bounded required_os_families.",
                    }
                ],
                "next_steps": ["Inspect known representations before any manual action."],
                "notices": [],
            }
        )

        self.assertEqual(view_model["status"], "evaluated")
        self.assertEqual(view_model["compatibility_status"], "compatible")
        self.assertEqual(view_model["host_profile"]["host_profile_id"], "windows-x86_64")
        self.assertEqual(view_model["primary_object"]["label"], "Compatibility Lab")
        self.assertEqual(view_model["source"]["family"], "synthetic_fixture")
        self.assertEqual(view_model["reasons"][0]["code"], "os_family_supported")

