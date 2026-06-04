from __future__ import annotations

import unittest

from runtime.surface.cache_key import build_surface_cache_key


class SurfaceCacheKeyTests(unittest.TestCase):
    def test_cache_key_changes_by_required_dimensions(self) -> None:
        base = _key(route="resolution_run", entity_id="run-1", profile="json_v0", posture="public")

        variants = [
            _key(route="search", entity_id="run-1", profile="json_v0", posture="public"),
            _key(route="resolution_run", entity_id="run-2", profile="json_v0", posture="public"),
            _key(route="resolution_run", entity_id="run-1", profile="text_v0", posture="public"),
            _key(route="resolution_run", entity_id="run-1", profile="json_v0", posture="operator_private"),
            _key(route="resolution_run", entity_id="run-1", profile="json_v0", posture="public", policy="operator_private"),
        ]

        for variant in variants:
            self.assertNotEqual(base["cache_key"], variant["cache_key"])

    def test_cache_key_records_explicit_placeholders(self) -> None:
        key = build_surface_cache_key(
            route="resolution_run",
            entity_id="run-1",
            view_model_version="surface_view_model.v0",
            representation_profile="json_v0",
            visibility_posture="public",
            policy_posture="public_read_only",
        )

        self.assertEqual(key["parts"]["renderer_id"], "renderer_unselected")
        self.assertEqual(key["parts"]["skin_id"], "default")
        self.assertEqual(key["parts"]["language"], "und")
        self.assertEqual(key["parts"]["data_version"], "unknown")


def _key(
    *,
    route: str,
    entity_id: str,
    profile: str,
    posture: str,
    policy: str = "public_read_only",
) -> dict[str, object]:
    return build_surface_cache_key(
        route=route,
        entity_id=entity_id,
        view_model_version="surface_view_model.v0",
        representation_profile=profile,
        visibility_posture=posture,
        policy_posture=policy,
    )


if __name__ == "__main__":
    unittest.main()
