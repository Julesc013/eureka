# TRACK-B-17 Source Cache To Evidence Bridge

This audit pack records the first bounded fixture-only bridge from local source cache records to local evidence ledger candidates.

The bridge follows the B-15 source cache runtime and B-16 evidence ledger runtime. It reads explicit committed source cache records, applies deterministic mapping policy, produces reviewable evidence candidate records, and preserves provenance, limitations, truth boundaries, and product boundaries.

The bridge cannot fetch live sources, run connectors, perform source sync, accept evidence, create public records, mutate the master index, create private local state, or make rights/malware/installability claims.

## Added

- `runtime/local_foundry/source_cache_to_evidence.py`
- `scripts/bridge_source_cache_to_evidence.py`
- `scripts/validate_source_cache_to_evidence_bridge.py`
- Bridge runtime, mapping, output, review, and path policies
- Bridge examples under `examples/source_cache_to_evidence/`
- Runtime and script tests
- Reference, architecture, and operations docs
- Generated audit evidence under `generated/`

## Review Boundary

Bridge output is not accepted truth. Every generated evidence record remains a candidate and requires review before candidate-store use, public index use, pack export, rights review, malware review, installability review, or master-index mutation.

## Validation

See `validation.md` for command results.

## Next

TRACK-B-18 - Local review queue runtime
