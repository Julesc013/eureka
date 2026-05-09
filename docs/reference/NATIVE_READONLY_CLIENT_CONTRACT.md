# Native Read-Only Client Contract

`contracts/native/native_readonly_client.v0.json` defines read-only native clients as consumers of local fixtures and governed contracts.

Current allowed behavior:

- read local snapshot fixtures
- read relay fixture envelopes
- display search, object, source, action, blocked-action, and diagnostic summaries
- show limitations and no-claims

Current forbidden behavior:

- live source calls or source sync
- downloads, mirroring, installs, execution, or emulation
- evidence, candidate, pack, source, action, or public truth acceptance
- public index or master index mutation
- accounts, uploads, telemetry, hosting, or public relay behavior
