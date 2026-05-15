# Leakage Baseline

The runtime architecture leakage gate remains at 1030 pre-existing
unallowlisted production findings.

LOCAL-11 did not increase this count.

The gate status is recorded as `fail` before and after because the repository
has the known pre-existing runtime leakage gate issue.

Full unittest discovery was run and failed for broader pre-existing suite issues
outside the LOCAL-11 focused lane, so the inventory records `fail_other`.
