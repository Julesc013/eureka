# Exec Plan

## Goal

Repair the imported AIDE Lite selftest fixture fallback so `test` and
`selftest` pass in Eureka without broad source-root import or product changes.

## Steps

1. Confirm repo identity, clean state, ignore rules, and Q26 handoff evidence.
2. Reproduce the exact failing `test` and `selftest` commands before editing.
3. Inspect `_write_minimal_repo`, Q19/Q20 optional file fallback behavior, and
   gateway/provider import checks.
4. Patch the temp-fixture fallback so missing optional `.py` files become valid
   inert Python modules or minimal offline helper modules inside the temporary
   selftest repo only.
5. Add focused `.aide/scripts/tests/**` coverage for the portable fallback.
6. Run AIDE Lite validation, regenerate next task/review packets, and record
   evidence.
7. Leave queue status as `needs_review`.

## Boundaries

- Allowed writes stay under `.aide/**` plus compact optional memory/status
  updates if needed.
- Do not copy AIDE `core/**` into Eureka.
- Do not change Eureka product source or product tests.
- Do not call providers, models, or network services.

## Current Status

- Baseline validation reproduced the failure.
- Root-cause diagnosis and repair are in progress.
