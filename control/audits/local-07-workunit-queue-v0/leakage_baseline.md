# Leakage Baseline

- before: 1030 new unallowlisted production findings
- after: 1030 new unallowlisted production findings
- LOCAL-07 increased leakage: false
- full unittest discovery status: fail_other
- follow-up: LOCAL-LEAKAGE-01

The runtime leakage gate remains a pre-existing warning. Full unittest discovery also
reported non-leakage validator failures from legacy task-packet and dirty-tree checks,
so it is recorded as fail_other rather than leakage-only.
