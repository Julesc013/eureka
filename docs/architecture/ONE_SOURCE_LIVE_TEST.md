# One Source Live Test

R0-09 proves the recovered runtime seams with one bounded public metadata source: the PyPI JSON metadata endpoint for `sampleproject`.

The source was selected because it is public, metadata-oriented, stable enough for a bounded smoke gate, and does not require package download, installation, execution, dependency solving, crawling, or private credentials. The only permitted live operation is one HTTP GET to `https://pypi.org/pypi/sampleproject/json` with an explicit User-Agent/contact posture.

The pipeline is:

1. Build a `SourceRecord` for `pypi_json_metadata`.
2. Evaluate source policy for `metadata_only`.
3. Build a `MetadataRequest`.
4. Capture the PyPI JSON response as a `MetadataResponse`.
5. Create a `SourceObservation`.
6. Create a `NormalizedObservation` with package name, version, summary, project URLs, and release count.
7. Persist the observation flow to `runtime/source/cache`.
8. Persist an evidence candidate to `runtime/evidence/ledger`.
9. Enqueue a review item in `runtime/review/queue`.
10. Record an explicit local review decision.
11. Rebuild `runtime/index/public` from accepted local review records.
12. Search the local reviewed index and produce an absence report for a missing query.

The reviewed index record is local workflow state. It is not source truth, evidence truth, legal approval, rights clearance, malware safety, exhaustive coverage, or production readiness.

Package file URLs may appear inside PyPI metadata. R0-09 records that metadata only; it never follows those URLs, never downloads wheels or source distributions, never installs a package, and never executes package code.

R0-09 writes only explicit local SQLite databases and audit artifacts under the requested audit output path. It does not mutate `site/`, `site/dist/`, a master index, source registries, connector registries, or runtime connector code.
