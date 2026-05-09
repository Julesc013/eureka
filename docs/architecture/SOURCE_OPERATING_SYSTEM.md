# Source Operating System

The Source Operating System is Eureka's reusable source-governance layer. It
defines source families, source records, capability descriptors, access modes,
index depth, trust lanes, operation policy, approval gates, fixtures, coverage
ledger expectations, scorecard expectations, and source-pack vocabulary.

It is not:

- a live connector runtime
- source sync
- a crawler
- a downloader
- accepted evidence
- public truth
- public or master index mutation

IA is the first reference pattern because it already exercised fixture
normalization, fail-closed live-probe gating, review integration, quality delta,
and postmortem without enabling live access.

H0-BUNDLE-01 keeps the layer descriptive. H0-BUNDLE-02 can add connector
interface, fixture replay, and live-probe envelope details without broad source
expansion.
