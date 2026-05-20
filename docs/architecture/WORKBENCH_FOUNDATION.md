# Workbench Foundation

WORKBENCH-FOUNDATION-00 defines Eureka Mission Control. The Workbench is the internal/operator superset of Eureka, not a throwaway admin page and not a public launch surface.

The Workbench is the proving ground for final backend and frontend behavior. Runtime services produce governed packets and view models, surfaces render those packets, and contracts define the packet authority. Workbench screens may expose richer operator-only fields and actions, but they must not invent separate product semantics.

Public web is a restricted projection of the same kernel and packets. API, CLI, and TUI are alternate projections. Relay, snapshot, native desktop, and mobile clients are later consumers of reviewed packets, snapshots, and capability profiles.

Mission Control modules are Search Console, Hunt Console, Source Lab, Evidence Studio, Candidate Review, Reviewed Index Builder, SYN Foundry, DOMAIN Pack Console, SCOUT Trail Console, Extraction Lab, Snapshot Console, Relay Console, and Ops/Audit Console.

This foundation does not implement HTTP routes, HTML pages, runtime behavior, Search Interaction, IA-HUNT bridge, SYN, extraction, downloads, uploads, model/provider calls, deployment, public fanout, production readiness, public launch readiness, full Archive.org integration, or marketplace/app-store readiness.
