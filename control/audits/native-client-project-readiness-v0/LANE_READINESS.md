# Lane Readiness

| Lane | Readiness | First Allowed Scope | Blockers | Build Host / Toolchain | Must Not Attempt Yet |
| --- | --- | --- | --- | --- | --- |
| `windows_7_x64_winforms_net48` | best first candidate after approval | read-only public data and seed snapshot inspection skeleton | explicit human approval, project path, UI scope, build host confirmation | Windows host with VS 2022 and .NET Framework 4.8 targeting; not verified by this review | downloads, installers, cache runtime, telemetry, FFI, live backend dependency |
| `windows_xp_x86_win32_unicode` | not ready; lab-verify | legacy read-only research after Windows 7 lane and toolchain review | v141_xp/toolchain availability, legacy UI constraints, TLS constraints | VS 2017 v141_xp or equivalent; unverified | modern TLS assumptions, live backend requirement, installer/download behavior |
| `windows_95_nt4_x86_win32_ansi` | not ready; lab-verify | thin text/file/snapshot browser research | VS6-era toolchain, ANSI constraints, dependency minimization | VS6-era or compatible lab host; unverified | Unicode-only assumptions, private data, live backend requirement |
| `windows_win16_research` | not ready; research only | future text/file/snapshot display research | host/runtime constraints, no native execution on x64/ARM64 Windows | Win16 research environment; unverified | native modern execution, live backend, installer/download behavior |
| `windows_modern_winui_future` | deferred | optional modern client later | lower priority than Windows 7 pragmatic lane | WinUI/Windows App SDK host; unverified | production claims, Rust backend replacement, installer automation |
| `macos_10_6_10_15_intel_appkit` | not ready; lab-verify | legacy Intel Mac read-only public data/snapshot candidate | Xcode 9.4-or-earlier matrix, i386+x86_64 support, host availability | macOS/Xcode lab host; unverified | Catalina-only assumptions, private data, live backend requirement |
| `macos_11_plus_modern` | deferred | optional modern macOS client later | lower priority than first Windows lane | modern macOS/Xcode host; unverified | production claims, installer/download behavior |
| `macos_10_4_10_5_ppc_intel_research` | not ready; research only | read-only snapshot/text/file research | PPC/i386 toolchain and runtime constraints | old Mac lab host; unverified | modern TLS assumption, live backend requirement |
| `classic_mac_7_1_9_2_research` | not ready; research only | future text/file/snapshot display research | CodeWarrior/classic runtime access, severe UI and filesystem constraints | classic Mac lab host; unverified | live backend, installer/download behavior, private data |

Lane conclusion: `windows_7_x64_winforms_net48` is the first future candidate,
but only for a minimal skeleton after explicit human approval. All other GUI
lanes remain deferred, lab-verify, or research.

