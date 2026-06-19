# Versioning And Compatibility

Existing v0 contracts are not broken in place.

Rules:

- additive-compatible fields may be added only where the schema permits them;
- breaking changes require a new version;
- projection versions may differ from core semantic versions;
- store migrations are separate tasks;
- replay/snapshot compatibility must name minimum supported versions;
- deprecation is not deletion;
- existing contracts are not moved for aesthetics.

