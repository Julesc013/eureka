# Native Surface

`surfaces/native/` is the home for native shells and shared native application assets.

The normal path uses governed contracts and gateway public APIs. A future dependency on `runtime/engine/sdk` is allowed only if Eureka explicitly adopts a bounded offline or local mode.

Bootstrap now includes a first local CLI slice under `surfaces/native/cli/` that proves a second surface family can reuse the same public-boundary and shared-mapping seams already exercised by `surfaces/web/`.

This CLI slice is stdlib-only, local-only, deterministic, and bootstrap-scale. It does not settle the long-term native, CLI, or TUI architecture.
