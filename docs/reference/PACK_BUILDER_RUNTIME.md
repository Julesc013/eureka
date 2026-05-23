# Pack Builder Runtime

Pack Builder Runtime v0 creates local pack drafts from explicit, committed,
repo-safe inputs. It can draft source, evidence, contribution, review, and
index-preview packs for later human review. A pack draft is portable review
material only.

This runtime is not pack import, pack submission, hosted upload, pack
acceptance, evidence acceptance, candidate acceptance, public truth, public
index mutation, or master-index mutation.

## Current Scope

- Explicit JSON inputs only.
- Local fixture and committed example records only.
- Standard-library runtime and CLI scripts.
- Writes no files unless an explicit output path is provided.
- Output paths are limited to `control/audits/**/generated/`,
  `examples/packs/drafts/`, or explicit temporary test directories.
- All draft output remains review-gated.

## Supported Current Draft Types

- `source_pack_draft`
- `evidence_pack_draft`
- `contribution_pack_draft`
- `review_pack_draft`
- `index_pack_preview`
- `policy_blocked_pack`

Future pack vocabularies such as compatibility, alias, hash, extraction,
query-need, and snapshot pack drafts are policy vocabulary only.

## Truth Boundary

Pack drafts must keep these values false: public truth, accepted evidence,
accepted pack, public-index mutation, master-index mutation, rights clearance,
malware safety, verified installability, exhaustive search, and production
readiness. Human review is required before import, submission, public use, or
index use.

## Validation

```bash
python scripts/validate_pack_builder_runtime.py
python scripts/build_local_pack.py --pack-type evidence_pack_draft --input examples/evidence/ledger/records/metadata_claim_record_v0.json --check
python scripts/summarize_local_pack.py --input examples/packs/drafts --check
```
