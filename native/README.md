# Eureka Native

`native/` is the canonical native client project root and skeleton lane.

Native work is not currently distribution-ready. Native clients are planned as
read-only consumers of snapshot, relay, and safe-action contracts. They must not
import Eureka Python internals, call source connectors, perform live probes,
download or execute artifacts, mutate stores, mutate public/master indexes,
accept truth, store credentials, enable accounts, or emit telemetry.

Directory names identify API or toolchain ownership. Support state, operating
systems, CPUs, IDEs, build hosts, and artifacts live in `native/matrix/`.

Current native posture is planning/skeleton evidence, not app-store,
marketplace, installer, or user-ready client behavior.
