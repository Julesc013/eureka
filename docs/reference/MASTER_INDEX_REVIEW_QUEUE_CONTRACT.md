# Master Index Review Queue Contract

Master Index Review Queue Contract v0 defines the governed review layer between
local/user/maintainer contribution packs and any future public Eureka master
index. It is contract, validation, and synthetic example work only. It does not
implement uploads, imports, moderation UI, accounts, hosted master-index
services, master-index writes, live probes, or automatic acceptance.
In plain terms: this contract does not implement uploads or hosted intake.

Contribution packs remain review candidates, not truth. Queue entries and
decisions preserve provenance, uncertainty, conflicts, and review posture before
any future public index state may be considered.

## Contract Files

- `contracts/master_index/review_queue_manifest.v0.json`
- `contracts/master_index/review_queue_entry.v0.json`
- `contracts/master_index/review_decision.v0.json`

The inventory files under `control/inventory/master_index/` define policy,
state taxonomy, and acceptance requirements. The synthetic example queue lives
under `examples/master_index_review_queue/minimal_review_queue_v0/`.

## Queue Manifest

`REVIEW_QUEUE_MANIFEST.json` describes a queue, entry files, decision files,
validation policy, privacy policy, rights policy, risk policy, conflict policy,
publication policy, and explicit no-runtime flags:

- `no_runtime_implemented: true`
- `no_upload_implemented: true`
- `no_accounts_implemented: true`
- `no_auto_acceptance: true`

Those flags are part of the contract posture. A valid v0 queue manifest cannot
pretend a hosted queue or account-backed review system exists.

## Queue Entry Model

A queue entry records:

- queue identity and contribution pack reference
- submitted pack lifecycle state
- validation status
- review status
- privacy, rights, and risk classification
- proposed changes
- referenced source/evidence/index/contribution packs
- evidence summary, including manual observations and AI suggestions if present
- conflict and dispute summary
- reviewer notes and limitations
- optional decision reference

Queue entries do not grant live network access, local filesystem access,
runtime import authority, or master-index mutation authority.

## Review Decision Model

Review decisions may:

- `accept_public`
- `reject`
- `quarantine`
- `request_revision`
- `supersede`
- `defer`

The v0 example uses `defer`. An `accept_public` decision, if used later, must
include explicit limitations and `public_claims_allowed` scope. It means limited
public claims may be candidates for a future master index with provenance; it
does not mean rights clearance, malware safety, or canonical truth.

## Validation Versus Review

Validation checks structure, checksums, parseability, private-path leakage,
secret fields, raw DB/cache files, executable payloads, and policy flags.

Review is a governance act. It considers privacy, rights, source policy, risk,
evidence provenance, conflict handling, and public-claim scope. Structural
validation alone is never acceptance.

## Privacy, Rights, And Risk

Queue entries classify privacy as `public_safe`, `local_private`,
`review_required`, `restricted`, or `unknown`.

Rights classifications include public metadata, source terms, review-required,
restricted, and unknown. Risk classifications distinguish metadata-only entries
from executable references, private-data risks, credential risks, and malware
review requirements.

Queue acceptance does not prove rights clearance or malware safety. It only
records that a future review process allowed a bounded public claim.

## Conflicts And Disputes

Conflicts are preserved as first-class data. A queue entry can record
conflicting references and dispute notes. Conflicts block automatic acceptance
and should not be flattened into a single source of truth without review.

## Pack Relationships

Source, evidence, index, and contribution packs may become queue inputs later.
Pack validation is not queue acceptance. Contribution packs wrap proposed
changes; the review queue records whether those proposals are deferred,
rejected, quarantined, revised, superseded, or accepted for limited public use.

## Manual Observations And AI Suggestions

Manual observations are accepted as references only when their observation
status and provenance are honest. Pending observations remain pending. AI
Provider Contract v0 now defines typed AI output boundaries: AI suggestions are
review candidates, not canonical evidence, truth, rights clearance, malware
safety, source trust, or automatic acceptance. Any future queue entry that
references AI output must preserve provider provenance, limitations, evidence
links where possible, and review status.

## Runtime Consumers

Future hosted public search, snapshots, native clients, and relay surfaces may
consume accepted public master-index outputs only after separate import,
review, and publication milestones. This contract does not add those consumers
or mutate the local/public search runtime.

Source/Evidence/Index Pack Import Planning v0 keeps pack import local and
separate from master-index review. Validate-only and local quarantine do not
submit, upload, accept, reject, supersede, publish, or mutate hosted/master
index state. A contribution can reach accepted_public only through a later
review decision with provenance and limitations.

Pack Import Validator Aggregator v0 now validates the review-queue example
through `python scripts/validate_pack_set.py --all-examples` or an explicit
`--pack-root`. Aggregated validation delegates to
`validate_master_index_review_queue.py` and does not implement queue import,
hosted queue runtime, review automation, or master-index writes.

## Validation Command

```powershell
python scripts/validate_master_index_review_queue.py
python scripts/validate_master_index_review_queue.py --json
python scripts/validate_master_index_review_queue.py --strict
```

The validator is stdlib-only and does not perform network calls.

## Not Implemented

- Queue runtime
- Upload handling
- Contribution import
- Source/evidence/index pack import
- Moderation UI
- Accounts, auth, identity, TLS, rate limiting, or telemetry
- Hosted master index
- Master-index writes
- Automatic acceptance
- Live source connectors or live probes
- Rights clearance, malware safety, canonical truth, or production readiness
  claims

## Next Work

Pack Import Validator Aggregator v0 and AI Provider Contract v0 are now
implemented as validation/contract-only milestones. The next recommended AI
follow-up is Typed AI Output Validator v0; the next pack-import follow-up is
Pack Import Report Format v0.
