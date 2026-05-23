# Pack Export Review

Pack Export review treats each exported pack as a draft artifact. Exporting
helps carry a pack draft to future review, but it does not make the pack
accepted, submitted, imported, published, signed, or public truth.

## Review Gates

- Review is required before pack import.
- Review is required before pack submission.
- Review is required before public use.
- Review is required before evidence acceptance.
- Review is required before public-index use.
- Review is required before master-index use.

Automatic import, submission, acceptance, evidence acceptance, public-index
mutation, and master-index mutation are disabled.

## Fixity And Signature Policy

SHA-256 fixity is required for each export. The runtime uses deterministic JSON
serialization and records an unsigned placeholder. Real signing, private keys,
and authenticity claims are forbidden in this milestone.

## Path Policy

Current outputs may be written only to `control/audits/**/generated/`,
`examples/packs/exports/`, or explicit temporary test directories. The runtime
must refuse `site/dist/`, `runtime/`, `contracts/`, `site/dist/data/public_index/`,
publication inventory roots, source inventory roots, hosted-submission roots,
and local private roots.

## Commands

```bash
python scripts/validate_pack_export_runtime.py
python scripts/export_local_pack.py --input examples/packs/drafts/evidence_pack_draft_v0.json --check
```
