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

AI provider outputs, if introduced later, must be treated as suggestions that
require evidence review. They do not become accepted records by themselves.

## Deferred Runtime

Future runtime work must separately specify hosted intake, local import
planning, queue storage, account or identity posture, moderation workflow,
publication, rollback, dispute handling, takedown handling, and audit retention.
This contract does not implement any of that behavior.
