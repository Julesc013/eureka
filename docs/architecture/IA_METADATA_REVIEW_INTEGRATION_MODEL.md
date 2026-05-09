# IA Metadata Review Integration Model

The IA review integration model is an adapter from connector outputs into the
Track B local review pipeline.

Flow:

```text
IA-BUNDLE-02 output
-> source-cache candidate review entry
-> evidence candidate review entry
-> candidate promotion dry-run
-> pack draft preview
-> quality delta
-> connector postmortem
-> H0 recommendation
```

Boundaries:

- The integration consumes explicit files only.
- The integration does not call networks, APIs, models, or providers.
- The integration does not mutate source cache, evidence ledger, review queue,
  public index, or master index runtime state.
- The integration keeps IA metadata as a source observation, not truth.

H0 should lift the reusable parts into a source operating system pattern:
source family registry, capability ladder, policy gate, fixture/replay harness,
live-probe envelope, source cache bridge, review queue bridge, coverage ledger,
and connector scorecard.
