# Client Consumption Guidance

Safe current use:

- Read `schema_version` first.
- Prefer stable public data roots under `public_site/data/`.
- Use `page_registry.json` for page/route display, not as live router
  discovery.
- Use `source_summary.json` for source labels, IDs, status, placeholder
  warnings, and coverage posture.
- Use `eval_summary.json` only as local audit/status evidence, not production
  relevance.
- Use `route_summary.json` only as public-alpha posture evidence, not GitHub
  Pages routing.
- Use `build_manifest.json` for diagnostics and disabled-behavior flags, not
  durable CI provenance.

Clients should not:

- treat public JSON as a production API
- infer live backend availability
- infer live probe availability
- infer deployment success
- infer external baseline observations
- infer malware safety or rights clearance
- branch on experimental capability details without version pinning
- consume internal repo path fields as public API
- display volatile counts or text as durable benchmarks

The minimum compatible future client should be able to show stable-draft fields
and limitation text while gracefully ignoring unknown, experimental, volatile,
internal, future, or deprecated fields.
