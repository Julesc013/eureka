# Build Host Requirements

A future skeleton implementation requires a Windows build host with:

- Visual Studio 2022
- .NET Framework 4.8 targeting pack or developer pack
- WinForms desktop workload support
- x64 build target
- ability to run or package for Windows 7 SP1+ x64 compatibility testing
- access to repo-local static data and seed snapshot files

The initial skeleton must not include:

- ClickOnce installer
- MSIX installer
- MSI installer
- package signing
- production signing
- network/live backend configuration
- external source credentials
- telemetry, analytics, or crash-report upload

The skeleton must keep no network/live backend behavior in scope.

The build host/toolchain is not verified by this planning milestone.
