# Local Source Cache Review

Local source cache records require review before downstream use. The review gate exists because a source observation can help plan future evidence work without becoming evidence or public truth.

Review is required before:

- evidence ledger bridge
- candidate store use
- public index use
- pack export
- source policy change
- live probe or connector runtime

Automatic evidence acceptance, public index use, master-index mutation, and connector enablement are forbidden in this milestone.

## Reviewer Checks

Reviewers should confirm that the record came from a committed fixture or repo-local source lead, contains no private paths or credentials, does not describe live source access, and keeps all truth and product boundary claims false. A blocked record should preserve the blocker instead of silently dropping it.

## Relationship To Evidence

Source cache records prepare future evidence-ledger bridge work. The bridge is not implemented here, and a source cache record cannot by itself create evidence, establish rights clearance, prove safety, prove installability, or mutate the master index.
