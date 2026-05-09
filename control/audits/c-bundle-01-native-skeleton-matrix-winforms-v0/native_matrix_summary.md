# Native Matrix Summary

The native matrix records first-wave lanes, future lanes, shared native libraries, host expectations, and artifact naming patterns.

First-wave lanes:

- `mac.carbon`
- `mac.appkit`
- `win.win32`
- `win.winforms`

Future lanes:

- `mac.swiftui`
- `win.win16`
- `win.winui`

Shared libraries:

- `lib.c89`
- `lib.objc`
- `lib.dotnet`

All lanes consume snapshot, relay, and action-manifest contracts. No lane consumes Python runtime internals or source connectors.
