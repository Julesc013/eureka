from __future__ import annotations

import unittest

from surfaces.web.workbench import render_bundle_inspection_html


class BundleInspectionRenderingTestCase(unittest.TestCase):
    def test_valid_bundle_inspection_rendering_includes_target_primary_object_and_members(self) -> None:
        html = render_bundle_inspection_html(
            {
                "status": "inspected",
                "inspection_mode": "local_offline",
                "source": {
                    "kind": "local_path",
                    "locator": "C:/tmp/demo-bundle.zip",
                },
                "bundle": {
                    "bundle_kind": "eureka.resolution_bundle",
                    "bundle_version": "0.1.0-draft",
                    "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                    "member_list": [
                        "README.txt",
                        "bundle.json",
                        "manifest.json",
                        "records/normalized_record.json",
                    ],
                },
                "primary_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                },
                "notices": [
                    {
                        "code": "bundle_inspected_locally_offline",
                        "severity": "info",
                        "message": "Inspected bundle locally and offline without live fixture access.",
                    }
                ],
            }
        )

        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("obj.synthetic-demo-app", html)
        self.assertIn("Synthetic Demo App", html)
        self.assertIn("bundle.json", html)
        self.assertIn("records/normalized_record.json", html)

    def test_invalid_bundle_inspection_rendering_includes_honest_error_content(self) -> None:
        html = render_bundle_inspection_html(
            {
                "status": "blocked",
                "inspection_mode": "local_offline",
                "source": {
                    "kind": "local_path",
                    "locator": "C:/tmp/bad-bundle.zip",
                },
                "notices": [
                    {
                        "code": "bundle_archive_invalid",
                        "severity": "error",
                        "message": "Bundle payload is not a valid ZIP archive.",
                    }
                ],
            }
        )

        self.assertIn("blocked", html)
        self.assertIn("C:/tmp/bad-bundle.zip", html)
        self.assertIn("bundle_archive_invalid", html)
        self.assertIn("Bundle payload is not a valid ZIP archive.", html)
