# Next Implementation Prompt Requirements

A future implementation prompt must:

- explicitly state that human approval has been granted
- cite this planning pack
- create only `clients/windows/winforms-net48/`
- use namespace `Eureka.Clients.Windows.WinForms`
- target Windows 7 SP1+ x64, WinForms, and .NET Framework 4.8
- keep all behavior read-only and demo-only
- consume only allowed static data and seed snapshot files
- include no network calls by default
- include no live backend or live probes
- include no downloads, installers, cache runtime, telemetry, accounts, relay,
  Rust FFI, or production claims
- add validation that project files remain in the approved path and scope

If human approval is not explicit, the next task should remain planning-only.

