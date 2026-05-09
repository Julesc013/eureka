# IA Bundle Sequence

## IA-BUNDLE-01 - IA Metadata Connector Foundation

Purpose: draft the source policy and connector gate packet, then add fixture
metadata normalization if approved by the IA-BUNDLE-01 scope.

Expected work:

- source policy draft
- User-Agent/contact decision packet
- rate-limit, timeout, retry, cache TTL, and kill-switch decision packet
- allowed endpoint and forbidden endpoint/action packet
- fixture metadata normalizer
- fixture/replay validation
- no live calls unless explicitly approved by a reviewed subgate

## IA-BUNDLE-02 - IA Bounded Metadata Live Probe

Purpose: run a bounded metadata-only probe only after IA-BUNDLE-01 approval.

Expected work:

- metadata-only call within the approved live-probe envelope
- source cache write
- evidence candidates
- review queue entries
- no downloads, uploads, account access, arbitrary URL fetch, mirroring, or
  public-query fanout

## IA-BUNDLE-03 - IA Reviewed-Index Dry-Run And Postmortem

Purpose: use reviewed records only to test the public-index rebuild contract as
a dry-run and produce a quality delta.

Expected work:

- reviewed records only
- reviewed-index dry-run
- search-quality delta report
- connector postmortem
- H0 readiness recommendation

## Source Operating System Compatibility

IA should become the reference connector pattern for future H0 and H1 source
families, not a one-off site connector. The pattern should preserve:

- source family
- source capability ladder
- source policy gate
- fixture/replay harness
- live-probe envelope
- source cache
- evidence candidate bridge
- review queue
- coverage ledger future
- connector scorecard future

IA-BUNDLE-00 does not implement H0.
