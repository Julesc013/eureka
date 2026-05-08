# Local Source Cache Runtime Plan

TRACK-B-13 defines the planning layer for a future local source cache. It does
not implement source-cache runtime, create local cache directories, fetch
sources, or write source-cache records.

## What It Is

A local source cache is a future local/private landing zone for reviewed source
observations and normalized source metadata. It may eventually hold approved
metadata observations, committed fixture observations, source lead summaries,
connector fixture outputs, source-health reports, source-policy decisions, and
source observation summaries.

The current milestone is planning-only. The active phase is
`phase_0_planning_only`, runtime status is `runtime_not_implemented`, and
source access status is `source_access_disabled`.

## What It Is Not

The local source cache is not accepted evidence, public truth, a public index,
the master index, live source sync, crawler storage, arbitrary URL cache, raw
payload storage, executable payload storage, credential storage, telemetry, or
production persistence.

Source cache records are observations or drafts. They must not claim rights
clearance, malware safety, verified installability, exhaustive global search, or
production readiness.

## Relationship To Existing Source Cache Work

`docs/reference/SOURCE_CACHE_CONTRACT.md` defines the source-cache contract
boundary. Existing P98 local dry-run source-cache tooling reports candidate
posture over committed examples only. B-13 does not replace either layer; it
adds the approval gates and runtime rollout plan that must be satisfied before
any future authoritative local source-cache runtime.

## Relationship To Candidate Store And Evidence Ledger

The candidate store can hold provisional source candidates. A future source
cache may normalize reviewed source observations. Evidence ledger conversion is
a later bridge task and must remain review-gated.

Current rule: source-cache output cannot become accepted evidence or public
truth. Future evidence ledger bridge work must produce evidence candidates only
until human review accepts them under a separate evidence policy.

## Source Access Modes

Current allowed modes:

- `committed_fixture_only`
- `repo_local_only`
- `manual_human_only`
- `no_autonomous_access`

Future deferred modes:

- `approved_metadata_probe_future`
- `approved_api_future`
- `approved_static_dump_future`
- `approved_common_crawl_or_archive_future`

Future modes require explicit source policy approval, operator approval,
User-Agent/contact decisions, rate limits, timeouts, retry policy, cache TTL,
kill switch, terms/robots review, privacy/risk review, and human review before
downstream evidence use.

Forbidden access includes Google result page scraping, unapproved forum
scraping, bulk Reddit ingestion, arbitrary URL fetch, credentialed access
without approval, captcha/paywall/access-control bypass, binary download, and
installer execution.

## Path And Storage Boundary

B-13 documents future roots but does not create them:

- `.aide.local/eureka/source_cache/`
- `.local/eureka/source_cache/`
- `.cache/eureka/source_cache/`

Current generated planning evidence may only use explicit audit output roots
such as `control/audits/**/generated/source_cache/` or explicit temporary test
directories. `site/dist/`, `runtime/`, `contracts/`, `native/`, `snapshots/`,
publication inventory, master-index-related roots, `.git/`, and private or
credential paths are forbidden output roots.

## Review Gates

Review is required before evidence ledger bridge, candidate store use, public
index use, pack export, source policy change, live probe, connector runtime, or
master-index-related work. Automatic evidence acceptance, public index use,
connector enablement, source sync, and master-index mutation are forbidden.

## Validation

```bash
python scripts/validate_local_source_cache_runtime_plan.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

The validator checks JSON syntax, current planning-only status, disabled source
access, future approval gates, path policy, examples, review gates, truth and
product boundaries, forbidden claims, private paths, and credential-shaped text.
