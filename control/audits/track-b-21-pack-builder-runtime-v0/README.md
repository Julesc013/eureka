# TRACK-B-21 Pack Builder Runtime

This audit records the first bounded local Pack Builder runtime. The runtime
builds review-gated pack drafts from explicit committed records and keeps pack
drafts separate from import, submission, acceptance, public-index mutation, and
master-index mutation.

## Added

- `runtime/local/foundry/pack_builder.py`
- `scripts/build_local_pack.py`
- `scripts/summarize_local_pack.py`
- `scripts/validate_pack_builder_runtime.py`
- Pack builder policies under `control/inventory/packs/`
- Pack builder request examples under `examples/packs/builder/`
- Pack draft examples under `examples/packs/drafts/`
- Reference, architecture, and operations docs for the runtime
- Runtime and operation tests for pack builder behavior

## Boundary

Pack drafts are portable review material only. They are not accepted packs,
accepted evidence, accepted public records, public-index mutations, or
master-index mutations. Pack import, submission, hosted upload, evidence
acceptance, candidate acceptance, source sync, live probes, downloads, uploads,
accounts, telemetry, and model/provider calls remain out of scope.

## Generated Evidence

The generated files in `generated/` were created from committed fixture
examples only:

- `sample_pack_draft.json`
- `sample_pack_builder_report.json`
- `sample_pack_builder_summary.md`

## Validation

Primary commands:

```bash
python scripts/validate_pack_builder_runtime.py
python scripts/build_local_pack.py --pack-type evidence_pack_draft --input examples/evidence/ledger/records/metadata_claim_record_v0.json --check
python scripts/summarize_local_pack.py --input examples/packs/drafts --check
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

Next recommended task: TRACK-B-22 - Pack export runtime.
