# Native Client Lanes

Native Client Lanes v0 records future Windows and Mac client candidates. This
is lane policy only. No Visual Studio project, Xcode project, native GUI,
installer, FFI layer, relay sidecar, or packaged runtime is implemented.

## Lane Summary

| Lane | Target | Stack | Status | First Scope |
| --- | --- | --- | --- | --- |
| `windows_7_x64_winforms_net48` | Windows 7 SP1+ x64 | WinForms / .NET Framework 4.8 / VS 2022 | future first candidate | Read-only public data and snapshot inspection prototype after review |
| `windows_xp_x86_win32_unicode` | Windows XP SP3+ x86 | Win32 Unicode / VS 2017 v141_xp | lab-verify | Legacy rich client research |
| `windows_95_nt4_x86_win32_ansi` | Windows 95+ / NT4+ x86 | Win32 ANSI / VS6-era | lab-verify | Thin file/text/snapshot browser research |
| `windows_win16_research` | Windows 3.1 / Win16 | Win16 research | research | Text/file/snapshot display research |
| `windows_modern_winui_future` | Windows 10/11 | WinUI / Windows App SDK | future/deferred | Optional richer modern Windows client |
| `macos_10_6_10_15_intel_appkit` | Mac OS X 10.6-10.15 Intel | AppKit / Objective-C / Xcode 9.4-or-earlier | lab-verify | Legacy Intel Mac candidate |
| `macos_11_plus_modern` | macOS 11+ | AppKit or SwiftUI | future/deferred | Optional modern macOS client |
| `macos_10_4_10_5_ppc_intel_research` | Mac OS X 10.4-10.5 PPC/i386 | AppKit / Objective-C research | research | Snapshot/text/file display research |
| `classic_mac_7_1_9_2_research` | Mac OS 7.1-9.2.2 Classic | CodeWarrior 68k/PPC research | research | Classic Mac display research |

The machine-readable lane registry is
`control/inventory/publication/native_client_lanes.json`.

Native Client Project Readiness Review v0 keeps this ordering and records
`windows_7_x64_winforms_net48` as the first candidate for a minimal skeleton
only after explicit human approval. No lane is approved for prototype behavior,
downloads, installers, cache runtime, telemetry, relay sidecars, live probes,
Rust FFI, or production claims.

Windows 7 WinForms Native Skeleton Planning v0 adds a planning pack for that
first lane only. It proposes the future path `clients/windows/winforms-net48/`
and namespace `Eureka.Clients.Windows.WinForms`, and keeps the initial scope
read-only/static-data/snapshot-demo only. The plan creates no project
directory, Visual Studio solution, `.csproj`, C# source, GUI behavior, FFI,
downloads, installers, cache runtime, telemetry, relay runtime, live probes, or
runtime wiring. A future skeleton implementation still requires explicit human
approval.

## Ordering Rationale

Windows 7 x64 WinForms is the first pragmatic native client candidate because
it can target an older but still practical desktop baseline with a familiar
toolchain. It is not implemented.

Windows XP and Windows 95/NT4 lanes are lab-verify because toolchain, Unicode,
TLS, and runtime assumptions need real host testing before any implementation
claim. They should degrade toward snapshots, text, files, and relay rather than
requiring a live API.

Win16 is research only. Win16 does not run natively on x64 or ARM64 Windows.

The Mac OS X 10.6-10.15 Intel lane remains lab-verify. Catalina does not force
a split by itself, but the exact 10.6-10.15 i386+x86_64 AppKit/Objective-C
toolchain remains unproven.

Catalina does not force a split by itself.

macOS 11+ is optional future work. Mac OS X 10.4-10.5 and Classic Mac lanes are
research only and should prefer snapshot/text/file/relay degradation.

## Shared Prohibitions

No lane may claim:

- implemented native GUI status
- production readiness
- executable trust
- installer automation
- package-manager mutation
- live backend availability
- live probe availability
- private data support by default
- Rust production backend or FFI availability

All lanes must wait for Native Action / Download / Install Policy v0 before
download, install, open, restore, or package-manager handoff behavior.
