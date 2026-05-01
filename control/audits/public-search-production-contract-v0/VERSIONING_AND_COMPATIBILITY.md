# Versioning And Compatibility

API route version: `/api/v1`.

Schema version: `0.1.0` for the current experimental contract set.

Stable-draft fields may receive additive optional fields. Removals, renames, or
semantic changes require a later compatibility note and validator update.

Old clients must be able to use GET query parameters, no-JS HTML handoff, lite
HTML, text surfaces, and public-safe JSON. P54 should emit compatibility
aliases such as `checked_sources` and `absence_summary` while introducing
production-facing names such as `checked` and `absence`.
