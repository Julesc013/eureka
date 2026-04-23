# Bounded Compatibility

This package holds Eureka's first bounded compatibility and host-profile seam.

It is intentionally small:

- it evaluates one resolved target against one bootstrap host profile preset
- it currently ships only a tiny fixed preset set such as `windows-x86_64`, `linux-x86_64`, and `macos-arm64`
- it carries compact requirement hints and compact verdict reasons
- it treats `unknown` as an honest first-class outcome
- it does not define a final compatibility oracle, installer model, runtime-routing engine, or policy system

The current model is designed to be easy to inspect and safe to carry through
normalize, a transport-neutral public boundary, and current surface projections.
