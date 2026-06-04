# SURFACE-KERNEL-00

This package records the minimal SurfaceKernel implementation.

The implementation adds checked-in runtime modules under:

```text
runtime/surface/**
```

The kernel adapts current resolver-run, fallback, public-search, and Workbench projection payloads into policy-filtered canonical view models and hands renderer-ready copies to a renderer dispatch boundary.

It does not implement full renderers, launch public alpha, add source providers, call sources, create reviewed records, or mutate indexes.

Next task: `BASELINE-RENDERERS-00`.
