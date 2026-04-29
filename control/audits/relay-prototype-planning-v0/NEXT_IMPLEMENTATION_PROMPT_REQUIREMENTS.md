# Next Implementation Prompt Requirements

A future Relay Prototype Implementation v0 prompt must explicitly state human
approval to create a runtime prototype.

It must also state:

- approved prototype id: `local_static_http_relay_prototype`
- approved bind scope
- approved implementation path
- approved input roots
- approved output routes
- no private data
- no writes/uploads/admin routes
- no live backend proxy
- no live source probes
- no downloads/installers/executable launch
- no telemetry/accounts
- required security tests
- required rollback/disable behavior

If explicit human approval is absent, the next prompt must remain planning or
review only.
