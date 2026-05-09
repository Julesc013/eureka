# Native Matrix Summary

Status: pass

## Lanes
- lib.c89: C89 / portable_c (contract_helper)
- lib.dotnet: .NET / future (placeholder)
- lib.objc: Objective-C / future (placeholder)
- mac.appkit: AppKit / Xcode 9.x (skeleton)
- mac.carbon: Carbon / CodeWarrior Pro 8/9 (skeleton)
- mac.swiftui: SwiftUI / Xcode future (future)
- win.win16: Win16 / Visual C++ future (future)
- win.win32: Win32 ANSI / Visual C++ 6.0 (skeleton)
- win.winforms: WinForms / Visual Studio 2022 (fixture_readonly_proof)
- win.winui: WinUI / Visual Studio future (future)

## Boundaries
- Native clients consume snapshot, relay, action, and view contracts only.
- Downloads, installs, execution, source sync, accounts, and telemetry remain disabled.
- No release binaries or build outputs are produced by this summary.
