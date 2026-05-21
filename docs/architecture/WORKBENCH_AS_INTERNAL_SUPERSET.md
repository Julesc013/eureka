# Workbench As Internal Superset

The Workbench is Eureka's internal/operator superset. It exercises the same kernel, contracts, packets, review flows, index machinery, source policies, and audit posture that later public and native projections consume.

Operator Workbench may show unsafe or mutable actions only when explicit policy and token posture allow them. Public and native clients restrict, hide, or make read-only those actions. They must not fork backend truth or define their own acceptance semantics.

Public web, public API, CLI, TUI, relay clients, snapshot clients, native desktop, and mobile clients are projections. They consume the same packet families with different permissions, density, and visibility.

This doctrine intentionally separates Workbench proof from production readiness. A working Workbench does not claim public hosting, broad Archive.org integration, downloads, extraction, model use, deployment, marketplace readiness, or app-store readiness.
