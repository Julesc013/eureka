# Surfaces

`surfaces/` contains Eureka's user-facing applications. Bootstrap keeps web and native separate so their dependency rules stay explicit.

- `web/` uses gateway public APIs and contracts in the normal online path
- `native/` uses contracts and gateway public APIs in the normal path, with any future engine SDK use explicitly gated to offline or local mode

Current bootstrap proof points:

- `web/` contains the compatibility-first HTML workbench slice
- `native/cli/` contains the first non-web surface slice, proving reuse across surface families without direct engine imports from the surface layer
