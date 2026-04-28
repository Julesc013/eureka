# Snapshot Surface Contract

Snapshot surfaces remain future/deferred as public routes. No public
`/snapshots/` artifact is published by the current GitHub Pages static site.

Signed Snapshot Format v0 now defines the first seed format and example under:

```text
snapshots/examples/static_snapshot_v0/
```

That seed example contains deterministic public data summaries, manifests,
checksums, and signature-placeholder documentation. It is not a production
signed release and it is not exposed as a public download surface.

Current boundary:

- snapshot format contract: implemented as experimental contract
- seed example: implemented under repo `snapshots/examples/static_snapshot_v0/`
- public `/snapshots/` route: future/deferred
- real signatures: future
- private signing keys: absent and prohibited
- executable downloads or software mirrors: absent and prohibited
- relay/native runtime behavior: future/deferred

Future public snapshot surfaces must remain static, deterministic, and safe to
copy. They must include manifests, checksums, signature metadata, source/eval
data provenance, and no private local paths. They must not imply live backend,
live probe, production API, or production signing availability.
