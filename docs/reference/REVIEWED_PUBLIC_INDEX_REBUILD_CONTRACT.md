# Reviewed Public Index Rebuild Contract

`contracts/master_index/reviewed_public_index_rebuild.v0.json` defines the future input and output shape for reviewed public-index rebuilds.

This contract is not a rebuild runtime. It does not write `site/dist/`, `site/dist/data/public_index/`, public search output, or master-index records. It defines what a later reviewed rebuild task must prove before any public-index mutation can be considered.

## Inputs

Future rebuild inputs may reference reviewed candidate promotion dry-runs, local review queue entries, candidate records, evidence ledger records, source cache records, source-cache-to-evidence bridge results, SearchNeed records, and future reviewed packs.

Forbidden inputs include unreviewed candidates, unreviewed evidence candidates, unreviewed source observations, private user files, credentials, executable downloads, installer payloads, account session data, and telemetry streams.

## Required Gates

Ready rebuild inputs must preserve:

- review refs or explicit limitations
- evidence refs where available
- source and provenance posture
- unresolved conflicts
- duplicate uncertainty
- rights, risk, identity, and compatibility blockers

Missing evidence, missing review, rights blocks, risk blocks, policy blocks, conflicts, and duplicate uncertainty must block or defer rebuild readiness.

## Outputs

Future outputs may include reviewed public record proposals, public search card candidates, preview manifests, limitation reports, no-claim summaries, blocker reports, and audit reports.

The current contract forbids public-index mutation, master-index mutation, accepted evidence truth without review, accepted candidate truth without review, rights clearance, malware safety, verified installability, exhaustive-search proof, and production-readiness claims.

## Validation

Run:

```bash
python scripts/validate_reviewed_public_index_rebuild_contract.py
python -m unittest tests.contracts.test_reviewed_public_index_rebuild_contract
```
