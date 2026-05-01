# Safety Defaults

P54 keeps these disabled or false:

- hosted backend deployed: false
- hosted deployment verified: false
- dynamic backend deployed: false
- no live probes
- no downloads
- no uploads
- no install actions
- no local paths
- no arbitrary URL fetch
- no telemetry
- no accounts
- no external calls
- no AI runtime

The wrapper rejects forbidden public-search parameters through the existing
gateway safety layer and does not mutate indexes, packs, staging state, or the
master index.
