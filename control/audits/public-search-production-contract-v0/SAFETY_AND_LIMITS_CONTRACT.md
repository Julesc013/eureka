# Safety And Limits Contract

P53 freezes these public limits:

- Maximum query length: 160.
- Default result limit: 10.
- Maximum result limit: 25.
- P54 hosted timeout budget: 5000 ms.
- Existing local runtime target: 3000 ms.

Forbidden behavior:

- no downloads
- no uploads
- no installs or execution
- no local paths
- no arbitrary URL fetch
- no live probes or source fanout
- no raw source payloads
- no stack traces
- no secret echo
- no telemetry by default
- no AI runtime

P54 must add rate-limit handling and an operator kill switch before exposure.
