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

Source/Evidence/Index Pack Import Planning v0 documents the future local import
boundary for these contracts. Validate-only must come before any private local
quarantine, and neither mode grants search, index, upload, hosted/master-index,
or automatic-acceptance authority.

Pack Import Validator Aggregator v0 provides one validate-only command for the
repo-owned examples:

```bash
python scripts/validate_pack_set.py --all-examples
```

The aggregate command delegates to the individual validators and does not
import, stage, index, upload, or accept packs.

Pack Import Report Format v0 adds `pack_import_report.v0.json` as the future
validate-only report envelope. Reports record validation outcomes, issues,
privacy/rights/risk posture, provenance, next actions, and hard false
mutation-safety fields. They do not import, stage, index, upload, mutate
runtime state, or mutate the master index.

AI Provider Contract v0 lives under `contracts/ai/`, not `contracts/packs/`.
AI outputs may later draft pack or contribution candidates only as typed,
review-required suggestions; they are not pack truth, rights clearance, malware
safety, or automatic acceptance.
