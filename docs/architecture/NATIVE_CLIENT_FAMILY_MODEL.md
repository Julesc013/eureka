# Native Client Family Model

Eureka native clients are consumers, not resolvers.

The native tree is organized by API and toolchain ownership: `mac/carbon`, `mac/appkit`, `win/win32`, `win/winforms`, and related library lanes. Support state, operating systems, CPUs, build hosts, and artifact plans live in `native/matrix/`.

C-BUNDLE-01 starts the family with:

- directory skeletons for first-wave and future lanes
- a fixture-oriented WinForms proof
- a portable C89 helper library
- native matrix contracts and validators

Native clients must not import Python runtime internals or connector logic. They consume snapshot, relay, action, and view contracts that already encode limitations and no-claims.
