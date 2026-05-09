# TRACK-B-22 Pack Export Runtime

This audit records the first bounded local Pack Export runtime. The runtime
exports explicit local pack drafts into review-gated export draft artifacts,
adds deterministic SHA-256 fixity, and records unsigned signature placeholders.

## Added

- `runtime/local_foundry/pack_export.py`
- `scripts/export_local_pack.py`
- `scripts/validate_pack_export_runtime.py`
- Pack export policies under `control/inventory/packs/`
- Pack export examples under `examples/pack_exports/`
- Reference, architecture, and operations docs for pack export
- Runtime and operation tests for pack export behavior

## Boundary

Exported packs are draft artifacts only. They are not imported, submitted,
uploaded, published, accepted, signed with real keys, accepted evidence,
accepted public records, public-index mutations, or master-index mutations.

## Fixity

Fixity is local SHA-256 over deterministic JSON bytes. It is not a real
signature and does not claim authenticity beyond local fixity.

## Generated Evidence

The generated files in `generated/` were created from committed fixture pack
draft examples only:

- `sample_pack_export.json`
- `sample_pack_export_report.json`
- `sample_pack_export_summary.md`

## Validation

Primary commands:

```bash
python scripts/validate_pack_export_runtime.py
python scripts/export_local_pack.py --input examples/pack_drafts/evidence_pack_draft_v0.json --check
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

Next recommended task: TRACK-B-23 - Track B integration audit.
