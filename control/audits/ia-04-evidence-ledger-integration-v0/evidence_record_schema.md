# Evidence Record Schema

IA evidence candidates include a stable evidence ID, source-cache record ID,
claim ID, claim kind, claim value, provenance, confidence, uncertainty,
limitations, and explicit boundary flags.

Required invariants:

- review required
- accepted truth false
- reviewer decision pending
- raw response committed false
- index mutation false
- download performed false

The shared durable ledger stores a sanitized payload while the IA audit output
keeps explicit boundary fields.
