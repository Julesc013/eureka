# Bounded Compatibility

This package holds Eureka's first bounded compatibility and host-profile seam.

It is intentionally small:

- it evaluates one resolved target against one bootstrap host profile preset
- it currently ships only a tiny fixed preset set such as `windows-x86_64`, `linux-x86_64`, and `macos-arm64`
- it carries compact requirement hints and compact verdict reasons
- it carries source-backed compatibility evidence records where bounded fixture
  metadata, member paths, README text, or compatibility notes support them
- it treats `unknown` as an honest first-class outcome
- it does not define a final compatibility oracle, installer model,
  runtime-routing engine, execution verifier, or policy system

The current model is designed to be easy to inspect and safe to carry through
normalize, a transport-neutral public boundary, and current surface projections.

Compatibility Evidence Pack v0 adds compact evidence records with typed
evidence kinds, claim types, normalized old-platform references, architecture
where available, confidence, locator, and source identity. It extracts only
from current committed fixture-backed records and preserves `unknown` when no
source-backed evidence exists. It does not execute software, verify installers,
call live sources, scrape external systems, or turn compatibility hints into
canonical truth.
