# Native Apps Later

Native app work is intentionally deferred until backend contracts and the hosted
alpha path are stronger.

## Current Policy

- no Visual Studio project yet
- no Xcode project yet
- no full native app work yet

Thin host shells may be explored later as experiments, but they should remain
downstream of stronger backend and public-boundary work.

Source Registry v0 does not change that policy by itself. Backend infrastructure
still takes priority over host shells.

Rust Migration Skeleton and Parity Plan v0 does not change that policy. The
Rust skeleton does not change that policy either: the workspace is a backend
parity lane only; it is not a native app project, does not add FFI, and does
not start host-shell work.

Rust Parity Fixture Pack v0 also does not change that policy. The Python-oracle
golden outputs are migration evidence for future backend seams; they are not a
native SDK, app shell, FFI layer, or runtime replacement.

## Host-Shell Principle

Future native apps should remain shells over the core. They should consume
public or SDK boundaries rather than re-implement resolver truth locally.

## Design Direction

When native work begins, the interaction model may be informed by:

- Mac App Store-style catalog and detail affordances
- Windows Marketplace or pre-Windows-Store distribution patterns

That design inspiration should not change the architectural rule that apps are
hosts over the resolver core rather than separate resolver implementations.

## Earliest Sensible Start

Serious native host work should wait until:

- source registry and planner shapes are clearer
- resolution runs exist
- local index work is underway
- public-alpha-safe boundaries are clearer
- Rust parity boundaries are clearer if native shells later consume Rust
  libraries directly
