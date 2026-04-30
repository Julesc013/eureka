# Future Implementation Sequence

Recommended sequence:

1. Pack Import Validator Aggregator v0 - implemented
2. Pack Import Report Format v0 - implemented
3. Validate-Only Pack Import Tool v0
4. Local Quarantine/Staging Model v0
5. Staged Pack Inspector v0
6. Local Index Candidate Import v0
7. Contribution Queue Candidate Export v0
8. Native Client Pack Import v0
9. Hosted Submission Intake v0, much later

Pack Import Validator Aggregator v0 should come first because the source,
evidence, index, contribution, and master-index review validators already
exist. A single safe command can identify pack type and run the right validator
before any import runtime, staging, or indexing authority exists.
