# Native Directory Policy

Native directory names identify API, language, or toolchain ownership.

Required roots include:

- `native/mac/carbon`
- `native/mac/appkit`
- `native/mac/swiftui`
- `native/win/win16`
- `native/win/win32`
- `native/win/winforms`
- `native/win/winui`
- `native/lib/c89`
- `native/lib/objc`
- `native/lib/dotnet`
- `native/matrix`

Support-state labels such as `legacy`, `modern`, `classic`, `old`, `new`, `universal`, `desktop`, `lite`, and `historical` are forbidden as directory names. Put support state in matrix files instead.
