from __future__ import annotations

import ast
import json
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from surfaces.native.cli.main import main


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
UNKNOWN_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"
SURFACE_NATIVE_CLI_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> tuple[int, str]:
    output = StringIO()
    exit_code = main(list(args), stdout=output)
    return exit_code, output.getvalue()


class NativeCliMainTestCase(unittest.TestCase):
    def test_resolve_known_target_returns_readable_output_with_resolved_resource_id(self) -> None:
        exit_code, output = run_cli("resolve", KNOWN_TARGET_REF)

        self.assertEqual(exit_code, 0)
        self.assertIn("Resolution", output)
        self.assertIn(f"target_ref: {KNOWN_TARGET_REF}", output)
        self.assertIn("resolved_resource_id: resolved:sha256:", output)
        self.assertIn("Synthetic Demo App", output)
        self.assertIn("Evidence", output)
        self.assertIn("label = Synthetic Demo App", output)
        self.assertIn("Known representations/access paths", output)
        self.assertIn("Synthetic demo app fixture artifact", output)

    def test_resolve_unknown_target_returns_honest_blocked_outcome(self) -> None:
        exit_code, output = run_cli("resolve", UNKNOWN_TARGET_REF)

        self.assertEqual(exit_code, 0)
        self.assertIn(f"target_ref: {UNKNOWN_TARGET_REF}", output)
        self.assertIn("status: blocked", output)
        self.assertIn("target_ref_not_found", output)

    def test_plan_command_renders_recommended_available_and_unavailable_actions(self) -> None:
        exit_code, output = run_cli("plan", "github-release:cli/cli@v2.65.0", "--host", "windows-x86_64")

        self.assertEqual(exit_code, 0)
        self.assertIn("Action plan", output)
        self.assertIn("target_ref: github-release:cli/cli@v2.65.0", output)
        self.assertIn("compatibility_status: compatible", output)
        self.assertIn("Recommended", output)
        self.assertIn("Access gh_2.65.0_windows_amd64.msi", output)
        self.assertIn("Available", output)
        self.assertIn("Export resolution manifest", output)
        self.assertIn("Unavailable", output)
        self.assertIn("Store resolution manifest locally", output)

    def test_resolve_github_target_includes_source_family_and_origin_summary(self) -> None:
        exit_code, output = run_cli("resolve", "github-release:cli/cli@v2.65.0")

        self.assertEqual(exit_code, 0)
        self.assertIn("target_ref: github-release:cli/cli@v2.65.0", output)
        self.assertIn("GitHub CLI 2.65.0", output)
        self.assertIn("family: github_releases", output)
        self.assertIn("label: GitHub Releases", output)
        self.assertIn("origin: https://github.com/cli/cli/releases/tag/v2.65.0", output)
        self.assertIn("version = v2.65.0", output)
        self.assertIn("GitHub CLI 2.65.0 release page", output)
        self.assertIn("gh_2.65.0_windows_amd64.msi", output)

    def test_search_returns_deterministic_results_and_resolved_resource_ids(self) -> None:
        exit_code, output = run_cli("search", "synthetic")

        self.assertEqual(exit_code, 0)
        self.assertIn("result_count: 2", output)
        self.assertLess(output.index("Synthetic Demo App"), output.index("Synthetic Demo Suite"))
        self.assertIn("resolved_resource_id: resolved:sha256:", output)

    def test_search_archive_returns_mixed_results_with_source_labels(self) -> None:
        exit_code, output = run_cli("search", "archive")

        self.assertEqual(exit_code, 0)
        self.assertIn("result_count: 4", output)
        self.assertIn("Archive Viewer", output)
        self.assertIn("ArchiveBox 0.8.5", output)
        self.assertIn("ArchiveBox v0.8.4", output)
        self.assertIn("ArchiveBox v0.8.5", output)
        self.assertIn("source: Synthetic Fixture", output)
        self.assertIn("source: GitHub Releases", output)
        self.assertIn("evidence: label via", output)

    def test_explain_resolve_miss_renders_compact_absence_report(self) -> None:
        exit_code, output = run_cli("explain-resolve-miss", "fixture:software/archivebox@9.9.9")

        self.assertEqual(exit_code, 0)
        self.assertIn("Absence report", output)
        self.assertIn("request_kind: resolve", output)
        self.assertIn("requested_value: fixture:software/archivebox@9.9.9", output)
        self.assertIn("likely_reason_code: known_subject_different_state", output)
        self.assertIn("checked_source_families: synthetic_fixture, github_releases", output)
        self.assertIn("Near matches", output)
        self.assertIn("fixture:software/archivebox@0.8.5", output)
        self.assertIn("github-release:archivebox/archivebox@v0.8.5", output)

    def test_explain_search_miss_returns_structured_absence_report(self) -> None:
        exit_code, output = run_cli("explain-search-miss", "archive box", "--json")
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["request_kind"], "search")
        self.assertEqual(payload["status"], "explained")
        self.assertEqual(payload["likely_reason_code"], "related_subjects_exist")
        self.assertEqual(payload["checked_source_families"], ["synthetic_fixture", "github_releases"])
        self.assertGreaterEqual(len(payload["near_matches"]), 3)
        self.assertEqual(payload["near_matches"][0]["subject_key"], "archivebox")

    def test_states_command_renders_ordered_state_list_with_source_and_resolved_ids(self) -> None:
        exit_code, output = run_cli("states", "archivebox")

        self.assertEqual(exit_code, 0)
        self.assertIn("Subject states", output)
        self.assertIn("status: listed", output)
        self.assertIn("subject_key: archivebox", output)
        self.assertIn("subject_label: ArchiveBox", output)
        self.assertIn("state_count: 3", output)
        self.assertIn("1. ArchiveBox 0.8.5", output)
        self.assertIn("2. ArchiveBox v0.8.5", output)
        self.assertIn("3. ArchiveBox v0.8.4", output)
        self.assertIn("resolved_resource_id: resolved:sha256:", output)
        self.assertIn("source_family: github_releases", output)
        self.assertIn("evidence: label via", output)

    def test_states_command_returns_blocked_shape_for_missing_subject(self) -> None:
        exit_code, output = run_cli("states", "missing-subject", "--json")
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["requested_subject_key"], "missing-subject")
        self.assertEqual(payload["notices"][0]["code"], "subject_not_found")

    def test_representations_command_renders_bounded_representation_list(self) -> None:
        exit_code, output = run_cli("representations", "github-release:cli/cli@v2.65.0")

        self.assertEqual(exit_code, 0)
        self.assertIn("Representations", output)
        self.assertIn("status: available", output)
        self.assertIn("target_ref: github-release:cli/cli@v2.65.0", output)
        self.assertIn("GitHub CLI 2.65.0 release page", output)
        self.assertIn("representation_kind: release_page", output)
        self.assertIn("gh_2.65.0_windows_amd64.msi", output)
        self.assertIn("access_kind: download", output)
        self.assertIn("source_family: github_releases", output)

    def test_compare_command_renders_agreements_disagreements_and_evidence(self) -> None:
        exit_code, output = run_cli(
            "compare",
            "fixture:software/archivebox@0.8.5",
            "github-release:archivebox/archivebox@v0.8.5",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Comparison", output)
        self.assertIn("status: compared", output)
        self.assertIn("target_ref: fixture:software/archivebox@0.8.5", output)
        self.assertIn("target_ref: github-release:archivebox/archivebox@v0.8.5", output)
        self.assertIn("Agreements", output)
        self.assertIn("subject_key = archivebox", output)
        self.assertIn("Disagreements", output)
        self.assertIn("object_label: ArchiveBox 0.8.5 != ArchiveBox v0.8.5", output)
        self.assertIn("Evidence", output)
        self.assertIn("version = v0.8.5", output)

    def test_compare_command_returns_blocked_shape_when_one_side_is_missing(self) -> None:
        exit_code, output = run_cli(
            "compare",
            "fixture:software/archivebox@0.8.5",
            UNKNOWN_TARGET_REF,
            "--json",
        )
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["left"]["status"], "completed")
        self.assertEqual(payload["right"]["status"], "blocked")
        self.assertEqual(payload["notices"][0]["code"], "comparison_right_unresolved")
        self.assertEqual(payload["right"]["notices"][0]["code"], "target_ref_not_found")

    def test_compatibility_command_renders_compatible_verdict(self) -> None:
        exit_code, output = run_cli(
            "compatibility",
            "fixture:software/compatibility-lab@3.2.1",
            "--host",
            "windows-x86_64",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Compatibility", output)
        self.assertIn("target_ref: fixture:software/compatibility-lab@3.2.1", output)
        self.assertIn("host_profile_id: windows-x86_64", output)
        self.assertIn("compatibility_status: compatible", output)
        self.assertIn("os_family_supported", output)
        self.assertIn("architecture_supported", output)

    def test_compatibility_command_can_return_unknown(self) -> None:
        exit_code, output = run_cli(
            "compatibility",
            KNOWN_TARGET_REF,
            "--host",
            "windows-x86_64",
            "--json",
        )
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "evaluated")
        self.assertEqual(payload["compatibility_status"], "unknown")
        self.assertEqual(payload["reasons"][0]["code"], "compatibility_requirements_missing")

    def test_plan_command_can_return_unknown_friendly_json(self) -> None:
        exit_code, output = run_cli(
            "plan",
            KNOWN_TARGET_REF,
            "--host",
            "windows-x86_64",
            "--json",
        )
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["compatibility_status"], "unknown")
        self.assertEqual(payload["compatibility_reasons"][0]["code"], "compatibility_requirements_missing")
        self.assertEqual(payload["actions"][0]["action_id"], "inspect_primary_representation")

    def test_manifest_export_returns_known_manifest_json(self) -> None:
        exit_code, output = run_cli("export-manifest", KNOWN_TARGET_REF, "--json")
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(payload["target_ref"], KNOWN_TARGET_REF)
        self.assertEqual(
            payload["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )
        self.assertEqual(payload["representations"][0]["representation_kind"], "fixture_artifact")
        self.assertEqual(payload["representations"][1]["access_kind"], "view")

    def test_bundle_export_returns_structured_summary_for_known_target(self) -> None:
        exit_code, output = run_cli("export-bundle", KNOWN_TARGET_REF, "--json")
        payload = json.loads(output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "exported")
        self.assertEqual(payload["target_ref"], KNOWN_TARGET_REF)
        self.assertEqual(payload["content_type"], "application/zip")
        self.assertEqual(payload["bundle_inspection"]["status"], "inspected")
        self.assertEqual(payload["bundle_inspection"]["bundle"]["target_ref"], KNOWN_TARGET_REF)

    def test_bundle_inspection_succeeds_for_valid_bundle_and_fails_honestly_for_missing_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_exit_code, store_output = run_cli(
                "store-bundle",
                KNOWN_TARGET_REF,
                "--store-root",
                temp_dir,
                "--json",
            )
            store_payload = json.loads(store_output)
            bundle_path = Path(temp_dir) / store_payload["artifact"]["store_path"]

            inspect_exit_code, inspect_output = run_cli("inspect-bundle", str(bundle_path), "--json")
            inspect_payload = json.loads(inspect_output)

            inspect_text_exit_code, inspect_text_output = run_cli("inspect-bundle", str(bundle_path))

            missing_exit_code, missing_output = run_cli(
                "inspect-bundle",
                str(Path(temp_dir) / "missing-bundle.zip"),
                "--json",
            )
            missing_payload = json.loads(missing_output)

        self.assertEqual(store_exit_code, 0)
        self.assertEqual(inspect_exit_code, 0)
        self.assertEqual(inspect_text_exit_code, 0)
        self.assertEqual(inspect_payload["status"], "inspected")
        self.assertEqual(inspect_payload["bundle"]["target_ref"], KNOWN_TARGET_REF)
        self.assertEqual(inspect_payload["evidence"][0]["claim_kind"], "label")
        self.assertEqual(inspect_payload["normalized_record"]["representations"][0]["representation_kind"], "fixture_artifact")
        self.assertIn("Evidence", inspect_text_output)
        self.assertIn("label = Synthetic Demo App", inspect_text_output)
        self.assertEqual(missing_exit_code, 0)
        self.assertEqual(missing_payload["status"], "blocked")
        self.assertEqual(missing_payload["notices"][0]["code"], "bundle_path_not_found")

    def test_store_list_and_read_commands_cover_manifest_and_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_output = json.loads(
                run_cli(
                    "store-manifest",
                    KNOWN_TARGET_REF,
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )
            bundle_output = json.loads(
                run_cli(
                    "store-bundle",
                    KNOWN_TARGET_REF,
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )
            listed_output = json.loads(
                run_cli(
                    "list-stored",
                    KNOWN_TARGET_REF,
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )
            read_manifest_output = json.loads(
                run_cli(
                    "read-stored",
                    manifest_output["artifact"]["artifact_id"],
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )
            read_bundle_output = json.loads(
                run_cli(
                    "read-stored",
                    bundle_output["artifact"]["artifact_id"],
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )

        self.assertEqual(manifest_output["status"], "stored")
        self.assertEqual(bundle_output["status"], "stored")
        self.assertEqual(
            [artifact["artifact_kind"] for artifact in listed_output["artifacts"]],
            ["resolution_bundle", "resolution_manifest"],
        )
        self.assertEqual(
            read_manifest_output["content"]["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )
        self.assertEqual(read_manifest_output["content"]["representations"][0]["representation_kind"], "fixture_artifact")
        self.assertEqual(read_bundle_output["artifact"]["artifact_kind"], "resolution_bundle")
        self.assertEqual(read_bundle_output["bundle_inspection"]["status"], "inspected")
        self.assertEqual(
            read_bundle_output["bundle_inspection"]["normalized_record"]["representations"][0]["representation_kind"],
            "fixture_artifact",
        )

    def test_store_list_and_read_plain_text_include_artifact_and_resolved_resource_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_exit_code, manifest_output = run_cli(
                "store-manifest",
                KNOWN_TARGET_REF,
                "--store-root",
                temp_dir,
            )
            bundle_output = json.loads(
                run_cli(
                    "store-bundle",
                    KNOWN_TARGET_REF,
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )
            artifact_id = bundle_output["artifact"]["artifact_id"]
            list_exit_code, list_output = run_cli(
                "list-stored",
                KNOWN_TARGET_REF,
                "--store-root",
                temp_dir,
            )
            read_exit_code, read_output = run_cli(
                "read-stored",
                artifact_id,
                "--store-root",
                temp_dir,
            )

        self.assertEqual(manifest_exit_code, 0)
        self.assertEqual(list_exit_code, 0)
        self.assertEqual(read_exit_code, 0)
        self.assertIn("artifact_id: sha256:", manifest_output)
        self.assertIn("resolved_resource_id: resolved:sha256:", manifest_output)
        self.assertIn(artifact_id, list_output)
        self.assertIn("resolved_resource_id: resolved:sha256:", list_output)
        self.assertIn("evidence: label via", list_output)
        self.assertIn(f"artifact_id: {artifact_id}", read_output)
        self.assertIn("resolved_resource_id: resolved:sha256:", read_output)
        self.assertIn("Evidence", read_output)
        self.assertIn("label = Synthetic Demo App", read_output)

    def test_cli_surface_end_to_end_flow_uses_public_boundary_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resolve_payload = json.loads(run_cli("resolve", KNOWN_TARGET_REF, "--json")[1])
            search_payload = json.loads(run_cli("search", "synthetic", "--json")[1])
            export_payload = json.loads(run_cli("export-manifest", KNOWN_TARGET_REF, "--json")[1])
            store_payload = json.loads(
                run_cli(
                    "store-bundle",
                    KNOWN_TARGET_REF,
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )
            bundle_path = Path(temp_dir) / store_payload["artifact"]["store_path"]
            list_payload = json.loads(
                run_cli(
                    "list-stored",
                    KNOWN_TARGET_REF,
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )
            inspect_payload = json.loads(run_cli("inspect-bundle", str(bundle_path), "--json")[1])
            read_payload = json.loads(
                run_cli(
                    "read-stored",
                    store_payload["artifact"]["artifact_id"],
                    "--store-root",
                    temp_dir,
                    "--json",
                )[1]
            )

        self.assertEqual(resolve_payload["workbench_session"]["active_job"]["status"], "completed")
        self.assertEqual(search_payload["result_count"], 2)
        self.assertEqual(export_payload["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(store_payload["artifact"]["artifact_kind"], "resolution_bundle")
        self.assertEqual(len(list_payload["artifacts"]), 1)
        self.assertEqual(inspect_payload["status"], "inspected")
        self.assertEqual(read_payload["bundle_inspection"]["status"], "inspected")

    def test_cli_surface_modules_do_not_import_engine_or_connector_internals(self) -> None:
        for path in SURFACE_NATIVE_CLI_ROOT.rglob("*.py"):
            if path.name.startswith("test_"):
                continue

            module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(module):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            alias.name.startswith("runtime.engine"),
                            f"{path} imports engine internals: {alias.name}",
                        )
                        self.assertFalse(
                            alias.name.startswith("runtime.connectors"),
                            f"{path} imports connector internals: {alias.name}",
                        )
                if isinstance(node, ast.ImportFrom) and node.module is not None:
                    self.assertFalse(
                        node.module.startswith("runtime.engine"),
                        f"{path} imports engine internals: {node.module}",
                    )
                    self.assertFalse(
                        node.module.startswith("runtime.connectors"),
                        f"{path} imports connector internals: {node.module}",
                    )
