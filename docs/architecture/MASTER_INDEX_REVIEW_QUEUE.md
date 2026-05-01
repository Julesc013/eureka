# Master Index Review Queue

The master index review queue is the future governance boundary between
review-candidate packs and public master-index state. It exists so Eureka can
preserve source/evidence provenance and review uncertainty before anything
affects hosted/public search.

In v0, this is a contract-only architecture slice. There is no hosted queue,
upload path, account system, moderation UI, queue worker, live probe, or
master-index writer.

## Flow

1. A source, evidence, index, or contribution pack validates locally.
2. A future queue entry references that pack and records proposed changes.
3. Structural checks, checksum checks, privacy scans, risk scans, and source
   policy checks run.
4. Reviewers or future policy-governed processes evaluate evidence,
   provenance, conflicts, rights posture, and publication scope.
5. A decision records defer, reject, quarantine, request revision, supersede, or
   limited accept-public posture.
6. Only future reviewed, public-safe, provenance-bound records can be candidates
   for hosted master-index publication.

## Governance Boundaries

Validation is not acceptance. Contribution is not truth. Acceptance is not
rights clearance, malware safety, or canonical proof.

The queue preserves disputes and conflicting claims instead of hiding them. A
conflict can block acceptance, request revision, or require quarantine.

## Relationships

Contribution packs are the main review-submission wrapper. Source, evidence,
and index packs provide supporting metadata, claims, observations, coverage, and
record-summary context. Public search, snapshots, native clients, and relay
surfaces should consume only later reviewed outputs, not raw queue entries.

AI Provider Contract v0 now defines future AI provider and typed-output
boundaries. AI outputs remain suggestions that require evidence review. They do
not become accepted records by themselves and cannot decide truth, rights,
malware safety, source trust, identity merges, or acceptance.

Typed AI Output Validator v0 adds `scripts/validate_ai_output.py` as an offline
pre-review check for those suggestions. Passing validation only means the
output shape, provider reference, required review, prohibited uses, and leakage
checks passed; it does not enter evidence, contribution, queue, or master-index
state automatically.

AI-Assisted Evidence Drafting Plan v0 may only create future candidates after
typed output validation and review. It does not implement model calls, queue
submission, automatic acceptance, hosted moderation, public-search mutation,
local-index mutation, or master-index mutation.

Source/Evidence/Index Pack Import Planning v0 keeps import local and
validate-only first. A staged pack is not submitted, uploaded, accepted,
published, or merged into the master index. Future queue export must be a
separate contribution/review step after private quarantine and inspection.

## Deferred Runtime

Future runtime work must separately specify hosted intake, local import
planning, queue storage, account or identity posture, moderation workflow,
publication, rollback, dispute handling, takedown handling, and audit retention.
This contract does not implement any of that behavior.
