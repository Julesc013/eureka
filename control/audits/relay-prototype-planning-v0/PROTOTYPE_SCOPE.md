# Prototype Scope

The recommended first prototype is:

`local_static_http_relay_prototype`

Future scope, if explicitly approved later:

- localhost bind only by default
- read-only
- serves allowlisted static public data and seed snapshot files only
- no live source calls
- no live backend proxying
- no private file roots
- no writes
- no uploads
- no admin routes
- no accounts
- no telemetry
- no installer or download automation
- no executable trust claims
- no public internet exposure
- no old-client private data exposure

This milestone does not implement that prototype. It only records the allowed
future shape and the gates that must pass before implementation.

The local static HTTP shape is preferred because it can be tested with Python
stdlib tooling later, maps naturally to existing static artifacts, can be
restricted to localhost, and avoids old/insecure protocol implementation in the
first prototype.
