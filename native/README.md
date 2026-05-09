# Eureka Native

This tree contains native-client skeletons and shared native contract helpers.

Native clients are read-only consumers of snapshot, relay, and safe-action
contracts. They must not import Eureka Python internals, call source connectors,
perform live probes, download or execute artifacts, mutate stores, mutate public
or master indexes, accept truth, store credentials, enable accounts, or emit
telemetry.

Directory names identify API or toolchain ownership. Support state, operating
systems, CPUs, IDEs, build hosts, and artifacts live in `native/matrix/`.
