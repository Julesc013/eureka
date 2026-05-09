# H1 Metadata Wave Model

H1 reuses H0 Source OS instead of inventing one-off connector rules.

Each source is represented as:

- source record
- source family assignment
- connector family assignment
- capability posture
- policy gate checklist
- endpoint class plan
- fixture plan
- output mapping plan
- coverage preview
- scorecard preview

The model keeps the distinction between source, connector, source observation, evidence, and public truth. A source record can say that a source exists and which family it belongs to. A connector family can say what adapter shape might fit. Neither grants permission to run live calls.

## Family Mapping

- `wayback_cdx_memento` uses `warc_cdx`, with `api_json` noted as an alternate shape for Memento metadata.
- `github_releases`, `software_heritage`, `repology`, and `osv` use `api_json`.
- `pypi` and `npm_registry` use `package_registry`, with `api_json` as an alternate.

## Future Work

H1-BUNDLE-02 may add committed fixtures and fixture-only normalizers. H1-BUNDLE-03 may add explicitly approved bounded live-probe envelopes. This bundle stops before both gates.
