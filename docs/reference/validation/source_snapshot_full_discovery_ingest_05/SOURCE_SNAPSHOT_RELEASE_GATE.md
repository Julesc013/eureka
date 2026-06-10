# Source Snapshot Release Gate

Status:

```text
blocked_current_full_discovery_failed
```

Evidence:

```text
source_snapshot_full_discovery_rerun_05
status: fail
tests_run: 5643
failures: 39
errors: 0
head: 9200df49f084cf313cccf821bf56f0194376f202
```

The external run is current to `dev` HEAD, but it is not green. The
source/snapshot release gate remains blocked until the classified failure family
is repaired and a later external full-discovery rerun is green for current HEAD.

