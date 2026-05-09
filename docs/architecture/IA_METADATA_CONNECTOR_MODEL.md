# IA Metadata Connector Model

The IA metadata connector foundation is a reference pattern for future source
families. It separates source policy, endpoint permission, fixture replay,
normalization, source-cache mapping, evidence preview mapping, and review.

## Flow

1. A committed fixture is loaded from `examples/connectors/internet_archive/fixtures/`.
2. The fixture boundary is checked for live-call, truth, and product violations.
3. Metadata is normalized into an IA source observation.
4. The normalized observation can be mapped to a source-cache candidate preview.
5. The normalized observation can be mapped to evidence candidate previews.
6. Later tasks may route reviewed candidates into review queues or dry-runs.

## Source Operating System Compatibility

The model preserves the H0 concepts without implementing H0:

- source family
- source capability ladder
- source policy gate
- fixture/replay harness
- live-probe envelope
- source cache
- evidence candidate bridge
- review queue
- future coverage ledger
- future connector scorecard

## No-Live Boundary

IA-BUNDLE-01 has no live-probe envelope execution. The envelope remains a
future approval target for IA-BUNDLE-02.
