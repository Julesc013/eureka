# Pack Builder Review

Pack Builder review treats every draft as provisional. A draft can help a human
review source, evidence, contribution, review, or index-preview material, but it
cannot bypass source, evidence, candidate, public-index, or master-index gates.

## Review Gates

- Review is required before pack import.
- Review is required before pack submission.
- Review is required before public use.
- Review is required before evidence acceptance.
- Review is required before public-index use.
- Review is required before master-index use.

Automatic import, submission, acceptance, public-index mutation, and
master-index mutation are disabled.

## Path Policy

Current outputs may be written only to `control/audits/**/generated/`,
`examples/pack_drafts/`, or explicit temporary test directories. The runtime
must refuse `site/dist/`, `runtime/`, `contracts/`, `site/dist/data/public_index/`,
publication inventory roots, source inventory roots, hosted-submission roots,
and local private roots.

## No-Goals

This milestone does not implement pack import, pack export, pack submission,
hosted upload, public review, evidence acceptance, candidate acceptance, public
index rebuild, master-index mutation, source sync, live probes, downloads,
uploads, accounts, telemetry, or model/provider calls.

## Commands

```bash
python scripts/validate_pack_builder_runtime.py
python scripts/build_local_pack.py --pack-type evidence_pack_draft --input examples/evidence_ledger_records/metadata_claim_record_v0.json --check
python scripts/summarize_local_pack.py --input examples/pack_drafts --check
```
