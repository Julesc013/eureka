# Manifest Format Summary

Local Staging Manifest Format v0 defines the future manifest envelope for
local/private quarantine staging. A future staging tool may write this manifest
only after a validate-only import report is reviewed and an operator explicitly
chooses staging.

Required sections record the validate-only report reference, staged pack
references, staged candidate entities, counts, privacy/rights/risk summaries,
provenance, hard no-mutation guarantees, reset/delete/export policy,
limitations, and notes.

The format is contract-only. No staging runtime exists, and no staged state is
created by this milestone.
