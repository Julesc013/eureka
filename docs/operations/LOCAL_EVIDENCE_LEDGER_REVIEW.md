# Local Evidence Ledger Review

Local evidence ledger records require review before downstream use. Review protects the boundary between a useful evidence candidate and accepted evidence.

Review is required before:

- candidate store use
- public index use
- pack export
- master-index use
- rights, malware-safety, or installability claims
- any future source-cache bridge

Automatic evidence acceptance, public index use, master-index mutation, rights clearance, malware safety, installability verification, conflict resolution, and merge are forbidden in this milestone.

## Reviewer Checks

Reviewers should confirm the record came from a committed fixture or repo-local example, contains no private paths or credentials, has a claim subject and provenance summary or explicit limitation, preserves conflicts, and keeps all truth and product boundary claims false.

## Relationship To Source Cache

Source cache records can be read as explicit inputs and represented as source observations, but the source-cache-to-evidence bridge runtime is not implemented here. Any bridge or promotion remains a future reviewed task.
