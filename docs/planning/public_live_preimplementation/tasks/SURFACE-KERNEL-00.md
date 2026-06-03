# SURFACE-KERNEL-00

Goal: implement or align the minimum SurfaceKernel for canonical view model
projection.

Inputs to read first: `architecture/SURFACE_KERNEL_SPEC.md`,
`docs/architecture/SURFACE_KERNEL.md`, representation contracts.

Allowed paths: `runtime/surface/**` if authorized, representation tests,
surface docs.

Protected paths: source adapters, review truth, deployment.

Deliverables: route resolution, capability negotiation, renderer dispatch,
output policy, cache key behavior.

Non-goals: renderer truth decisions, source calls, public launch.

Validation: representation contract tests, renderer parity harness, public
route tests.

Exit criteria: renderers project filtered view models only.

Impact statement: runtime/surface and representation impact.

