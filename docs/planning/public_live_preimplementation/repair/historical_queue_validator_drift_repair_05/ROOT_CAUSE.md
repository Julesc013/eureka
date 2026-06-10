# Root Cause

The rerun 05 failures came from stale queue posture expectations in historical validators.

Those validators were written while the relevant HUNT, LOCAL, public-alpha defer, and promotion tasks were active or immediately succeeded by older tasks. The current queue has advanced to external evidence and hardware-detail waiting states:

```text
WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE
WAITING_FOR_USER_HARDWARE_DETAILS
```

The old validators interpreted that current posture as a missing successor or failed promotion state even though the historical task artifacts remained complete.

This was validator expectation drift, not a runtime/product behavior regression.

