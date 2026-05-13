# Local Appliance Model

The Local Appliance is the product kernel for Eureka before F0 continues. R0 recovered durable seams for source observations, source cache, evidence ledger, review queue, and reviewed public index. LOCAL adds the missing local machine-hosted loop that proves those seams as a usable product surface.

The model has five layers:

- Instance: an explicit local instance root, config, schema, migration guard, and no hidden state roots.
- Store: durable local stores for reviewed index, source cache, evidence ledger, review queue, WorkUnits, sessions, and eval records.
- Service: localhost-first HTTP access, read-only by default, with LAN disabled unless a future explicit gate enables it.
- Worker: deterministic WorkUnit execution only, with typed outputs routed through stores and review.
- Workbench: an HTML operator surface for search, sessions, WorkUnits, evidence review, index rebuilds, smoke tests, and evals.

LOCAL-00 does not implement any of those runtime layers. It makes them mandatory before F0 and later tracks claim completion.
