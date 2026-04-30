# Future Import Pipeline Impact

The aggregate validator is the first safe reusable step for a future
validate-only import pipeline.

Future use:

1. identify pack type
2. run the aggregate validator or the delegated individual validator
3. emit a pack import report
4. stop without staging or mutation

Still future:

- Pack Import Report Format v0
- Validate-Only Pack Import Tool v0
- Local Quarantine/Staging Model v0
- Staged Pack Inspector v0
- Local Index Candidate Import v0
- Contribution Queue Candidate Export v0

The aggregate validator does not itself implement any of those future modes.

