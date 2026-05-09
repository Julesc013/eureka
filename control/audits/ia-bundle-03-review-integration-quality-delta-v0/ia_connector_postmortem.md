# IA Connector Postmortem

What worked:

- IA-BUNDLE-01 fixture normalization feeds review-shaped artifacts.
- IA-BUNDLE-02 fail-closed blocked outputs are reviewable without inventing live
  evidence.
- IA-BUNDLE-03 can rehearse review, promotion dry-run, pack preview, and quality
  delta while preserving boundaries.

What failed:

- The live metadata probe is still blocked because operator approval is missing.

H0 implications:

- Source registry, capability ladder, source policy gate, fixture/replay
  harness, live-probe envelope, coverage ledger, and connector scorecard should
  become shared Source OS primitives before H1 expansion.

Future connectors are not automatically approved by this postmortem.
