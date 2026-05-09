# Pack Export Runtime

Pack Export Runtime v0 turns an explicit local pack draft into an export-form
draft artifact. It normalizes export metadata, computes local SHA-256 fixity,
adds unsigned signature placeholders, preserves review gates, and writes only
when an explicit approved output path is provided.

Pack Export is not pack import, submission, upload, publication, acceptance,
public truth, evidence acceptance, candidate acceptance, public-index mutation,
master-index mutation, or real cryptographic signing.

## Current Scope

- Explicit `local_pack_draft.v0` JSON input only.
- Local fixture and repo example drafts only.
- Standard-library runtime and CLI script.
- Writes no files by default.
- Output roots are limited to `control/audits/**/generated/`,
  `examples/pack_exports/`, and explicit temporary test directories.

## Current Export Types

- `source_pack_export`
- `evidence_pack_export`
- `contribution_pack_export`
- `review_pack_export`
- `index_pack_preview_export`
- `policy_blocked_pack_export`

Future signed, archive, snapshot, and hosted submission package formats are
policy vocabulary only.

## Fixity

The runtime computes SHA-256 over deterministic JSON bytes with fixity and
manifest fields empty. The hash is local fixity only. It is not a real
signature and does not prove authenticity beyond the local exported bytes.

## Validation

```bash
python scripts/validate_pack_export_runtime.py
python scripts/export_local_pack.py --input examples/pack_drafts/evidence_pack_draft_v0.json --check
```
