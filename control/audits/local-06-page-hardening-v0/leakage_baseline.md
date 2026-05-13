# Leakage Baseline

LOCAL-06 records the pre-existing runtime leakage gate state without increasing it.

- before: fail with 1030 new unallowlisted production findings
- after: fail with 1030 new unallowlisted production findings
- increased leakage: false
- full unittest discovery: fail_other
- follow-up: LOCAL-LEAKAGE-01

This is a known warning from earlier LOCAL work and is not introduced by page hardening.
