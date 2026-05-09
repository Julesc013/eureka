# Snapshot Manifest Contract

`contracts/snapshots/snapshot_manifest.v0.json` defines deterministic offline snapshot contents.

The manifest includes normalized snapshot records, record counts, type counts, source/evidence/action summaries, render targets, fixity entries, signature posture, limitations, no-claims, and boundaries.

Manifests are public-safe fixture projections. They are not source authenticity, accepted evidence, accepted candidate truth, public index state, or master index state.

Validation:

```powershell
python -m json.tool contracts/snapshots/snapshot_manifest.v0.json
python scripts/build_snapshot_fixture.py --input examples/snapshots/fixtures/search_snapshot_input_v0.json --check
```
