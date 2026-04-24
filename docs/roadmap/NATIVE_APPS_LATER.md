# Native Apps Later

Native app work is intentionally deferred until backend contracts and the hosted
alpha path are stronger.

## Current Policy

- no Visual Studio project yet
- no Xcode project yet
- no full native app work yet

Thin host shells may be explored later as experiments, but they should remain
downstream of stronger backend and public-boundary work.

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
