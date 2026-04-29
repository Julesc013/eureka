# Next Guards

Recommended next milestone:

1. Generated Artifact Drift Guard v0

Scope for that guard:

- compare `public_site/data/` against generator output
- compare `site/dist/data/` against generator output
- check public-data stability report coverage when public JSON files change
- check lite/text/files surfaces against public data inputs
- check static resolver demo data against current goldens
- check static snapshot seed contents and checksums
- ensure no generated artifact claims live backend, live probes, external
  observations, production signing, downloads, installers, telemetry, accounts,
  or deployment success

Other safe follow-ups:

- Snapshot Consumer Tooling Plan v0
- Search Usefulness Source Expansion v2, fixture-only
- Manual Observation Batch 0 Execution, human-operated
- Rust Local Index Parity Candidate v0 only after review and Cargo availability
- Windows 7 WinForms skeleton implementation only after explicit human approval
