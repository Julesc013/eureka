# Pack Contracts

`contracts/packs/` defines governed portable bundle formats for future
extension and contribution workflows.

Current pack contracts are contract and validation assets only. They do not
implement import, indexing, merge, upload, raw database export, executable
plugins, live connectors, hosted submission, or master-index acceptance.

## Current Contracts

- `source_pack.v0.json` - manifest schema for Source Pack Contract v0. Source
  packs carry source metadata, public-safe evidence inputs, tiny deterministic
  fixtures, rights/privacy notes, and checksum declarations.
- `evidence_pack.v0.json` - manifest schema for Evidence Pack Contract v0.
  Evidence packs carry public-safe claims, observations, source locators, short
  snippets, compatibility notes, member notes, absence notes, provenance, and
  checksum declarations.
- `index_pack.v0.json` - manifest schema for Index Pack Contract v0. Index
  packs carry index-build metadata, source coverage, field coverage, query
  examples, public-safe record summaries, and checksum declarations without raw
  cache or database export.
- `contribution_pack.v0.json` - manifest schema for Contribution Pack Contract
  v0. Contribution packs carry review-candidate items, optional references to
  source/evidence/index packs, manual-observation placeholders, metadata
  corrections, alias suggestions, compatibility suggestions, absence reports,
  result feedback, and checksum declarations without upload/import authority.

Master-index review queue contracts now live under `contracts/master_index/`
because queue entries and decisions are governance records, not pack formats.
Pack contracts must stay separate so one pack type cannot silently gain the
authority of another.
