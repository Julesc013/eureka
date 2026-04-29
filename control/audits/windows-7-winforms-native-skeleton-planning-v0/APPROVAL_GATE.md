# Approval Gate

Human approval is required before any implementation.

Approval must explicitly confirm:

- project path: `clients/windows/winforms-net48/`
- namespace: `Eureka.Clients.Windows.WinForms`
- lane: `windows_7_x64_winforms_net48`
- build host availability
- Visual Studio 2022 availability
- .NET Framework 4.8 targeting pack/developer pack availability
- x64 target
- read-only/demo-only scope
- no downloads or installers
- no local cache runtime or private file ingestion
- no telemetry, accounts, or cloud sync
- no relay runtime
- no live backend dependency
- no live source probes
- no Rust FFI
- no production claims

Unsigned or implicit approval is not sufficient. A future implementation prompt
must cite this gate and record the approval source.

