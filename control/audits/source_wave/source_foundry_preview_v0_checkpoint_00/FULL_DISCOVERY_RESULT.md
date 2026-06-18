# External Full Discovery Result

Task: `SOURCE-FOUNDRY-PREVIEW-V0-CHECKPOINT-00`

Run id: `source_foundry_preview_v0_checkpoint_00`

Status: `fail`

Generated from compact artifacts returned by the external full-discovery
harness. Raw unittest logs are not committed.

## Summary

- command: `python -m unittest discover -s tests -t .`
- git branch: `dev`
- git head: `670a573276d220d8136942de38eed4e0115749a5`
- working tree clean during run: true
- tests run: 5792
- failures: 43
- errors: 7
- failed tests: 50
- failed modules: 40
- failure families: 31
- elapsed seconds: 3244.023
- exit code: 1

## Compact Artifact Hashes

- `full_unittest_summary.json`: `sha256:964241ab75e74ec1b48dbd0a45bb9c81e2c5ead7feac49bda04def8709772a0c`
- `failure_families.json`: `sha256:e2f85171bc67c6c8283a2ed00a42c8d38d41e2b8516921e0ed2917566b8c682e`
- `failed_tests.txt`: `sha256:38638a1be321b938be5cb51ed0c743cb8b740e200f366017074b68e92277e8d6`

## Triage

The red result is broad-discovery validator drift, not a reviewed-truth or
public-exposure event.

Representative failure classes:

- historical HUNT queue-state validators expecting HUNT-era queue/task packets;
- historical LOCAL queue-state validators expecting LOCAL-era queue/task packets;
- public-alpha/defer validators expecting older public-alpha queue states;
- dev-to-main promotion validators expecting `origin/main` and `origin/dev` to
  already match;
- repository layout/canon validators returning nonzero;
- runtime leakage/staging validators reporting pre-existing or historical
  findings.

The live queue is intentionally on `REVIEW-IA-CANDIDATES-BATCH-00`, so older
operation tests that assert a single historical `current_recommended_task`
cannot be treated as current source-foundry product failures without a repair or
policy update.

## Boundary

- `dev -> main` promotion performed: false
- review decisions recorded: false
- review ledger events written: 0
- reviewed records created: false
- reviewed/master mutation: false
- public-index mutation: false
- snapshot refresh: false
- public exposure changed: false
- license posture changed: false
- reviewed IA truth claimed: false

## Decision

`dev -> main` promotion remains blocked.

Recommended next lane:

```text
SOURCE-FOUNDRY-PREVIEW-V0-FULL-DISCOVERY-DRIFT-TRIAGE-00
```

That lane should decide whether the failing historical validators need repair,
retirement, scope gating, or promotion-gate reclassification before another
external full-discovery run.
