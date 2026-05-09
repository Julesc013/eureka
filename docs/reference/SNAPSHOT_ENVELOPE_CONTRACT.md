# Snapshot Envelope Contract

`contracts/snapshots/snapshot_envelope.v0.json` defines the outer wrapper for a fixture/local offline snapshot.

The envelope names the manifest, record refs, fixity report, signature envelope, verification report, render results, source refs, evidence refs, action refs, limitations, no-claims, truth boundary, and product boundary.

Current envelopes are fixture/local only. They do not publish, host, relay, download, mirror, execute, mutate indexes, or accept evidence, candidates, sources, actions, packs, or public truth.

Validation:

```powershell
python -m json.tool contracts/snapshots/snapshot_envelope.v0.json
python scripts/validate_snapshot_runtime.py
```
