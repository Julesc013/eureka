## Bounded Representation Selection and Handoff

`runtime/engine/handoff/` holds the first bounded representation-selection and
handoff seam for Eureka.

This slice is intentionally small. It takes:

- one already resolved target
- bounded known representations and access paths
- an optional bootstrap host profile
- an optional bootstrap strategy profile

and returns:

- one preferred bounded fit when the current signals support that choice
- alternatives that remain available
- unsuitable or unknown choices with compact reasons

This is not:

- a downloader
- an installer
- a launcher
- a restore or import workflow
- a ranking engine
- a final policy or runtime-routing model

The current rules are deterministic, heuristic, and replaceable. They exist to
prove that Eureka can make a bounded representation handoff recommendation
without silently discarding alternatives or pretending to execute them.
