# Leakage Baseline

The runtime leakage gate remains a pre-existing failure with 1030 new
unallowlisted production findings. LOCAL-10 does not add runtime leakage in
`runtime/local/eval`.

Status is therefore pass with warnings for the LOCAL-10 validator. Full unittest
discovery was attempted and failed outside the focused LOCAL-10 lane, so the
baseline records `fail_other`.
