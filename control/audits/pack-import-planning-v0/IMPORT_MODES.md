# Import Modes

Future pack import should begin with the least powerful mode and only add more
authority through separate milestones.

## 1. validate_only

Default first implementation target.

The tool runs the relevant pack validators, writes an import report, and makes
no staging, search, index, registry, or hosted changes.

## 2. stage_local_quarantine

Future follow-up mode.

The tool records validated pack metadata and validation reports under a
user-controlled local staging or quarantine root. It does not affect search or
index results.

## 3. inspect_staged

Future follow-up mode.

The user can inspect staged pack metadata, claims, summaries, provenance, and
validation results. It remains read-only and does not mutate canonical records.

## 4. local_index_candidate

Future opt-in mode, not implemented now.

Public-safe staged records may be included in a local-only index build only
after explicit import and index milestones. This must not change hosted search,
static public search, or the canonical source registry.

## 5. contribution_queue_candidate

Future opt-in mode, not implemented now.

Validated staged records may be wrapped into contribution-pack or review-queue
candidates. This is not upload, submission, or acceptance.

## 6. rejected_or_quarantined

Invalid, unsafe, privacy-risky, rights-unclear, executable-bearing, raw-cache,
or uncertain packs are rejected or quarantined. Quarantine preserves evidence
for local review and does not imply public eligibility.

