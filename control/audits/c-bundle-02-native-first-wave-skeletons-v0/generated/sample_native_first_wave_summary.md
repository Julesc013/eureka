# Native First-Wave Summary

Status: pass

## Lanes
- win.win32: Win32 ANSI / Visual C++ 6.0 (manual_build_required)
- mac.appkit: AppKit / Xcode 9.x (manual_build_required)
- mac.carbon: Carbon / CodeWarrior Pro 8/9 (manual_build_required)

## Boundaries
- Win32, AppKit, and Carbon skeletons are read-only fixture consumers.
- Downloads, installs, execution, source sync, accounts, telemetry, and index mutation remain disabled.
- Build evidence is manual/future; no build outputs or release binaries are committed.
