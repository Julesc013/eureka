# Security And Abuse Review

- route ID length cap
- route ID charset policy
- no path traversal
- no arbitrary URL fetch
- no local file access
- no source selector that triggers live calls
- no private cache access
- stable error envelope
- rate-limit/edge requirement for hosted runtime
- no telemetry/account tracking by default
- operator kill switch
