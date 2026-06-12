# Root Cause

The rerun 08 failures were caused by stale historical validator expectations
after the queue advanced past earlier HUNT, promotion, and public-alpha defer
sequences into the IA metadata provider smoke and external validation chain.

The validators were still looking for older current task successors or old
post-promotion branch assumptions. The current repo state is instead:

```text
IA metadata provider smoke completed
rerun 08 ingested as red
repair task HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
next external validation rerun 09
```

This is not:

```text
runtime/product failure
IA metadata provider failure
SurfaceKernel failure
provider behavior failure
artifact evidence failure
```

