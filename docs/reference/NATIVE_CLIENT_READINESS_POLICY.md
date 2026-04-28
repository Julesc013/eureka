# Native Client Readiness Policy

Native app projects remain deferred. The current local native-style surface is
the CLI/local scripts path, not a packaged Windows or macOS app.

Prerequisites before native GUI client work starts:

- stable-enough public data contracts
- static export and snapshot format contracts
- live backend handoff contract for optional online mode
- source, evidence, result-lane, action, and absence models stable enough for
  client consumption
- rights/security/download policy before any fetch/install workflow
- clear local-cache and offline snapshot semantics
- no dependency on private engine internals

Installer automation remains deferred until rights, security, executable-risk,
hash/checksum, and action-handoff policies exist.

Future Windows and macOS lane docs may define prototypes later, but they must
consume governed public data, snapshots, or live handoff contracts. They must
not become a back door into runtime internals.
