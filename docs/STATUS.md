# Status

This page carries current-state detail that should not dominate the public
front door. The root [README](../README.md) explains what Eureka is; this page
summarizes what is real now, what is gated, and where to look next.

## Current Maturity

Eureka is a local-first Python reference backend and prototype. The current
product objective is `EUREKA-REAL-LIVE-SEARCH-HUNT-00`:

```text
arbitrary live query
-> immediate transient web leads
-> deeper Hunt
-> safe page inspection
-> durable local Preview Index
-> restart
-> local search
```

The first reset/foundation work is present, but Eureka is not yet a functional
end-to-end search engine. Safe fetch, extraction, durable live indexing, real
budgeted Hunt, and unseen-query human acceptance remain incomplete.

Eureka has not been deployed, has not launched publicly, and does not claim
production readiness.

## Branch Posture

| Topic | Current posture |
| --- | --- |
| Normal development branch | `dev` |
| Current product task | `EUREKA-REAL-LIVE-SEARCH-HUNT-00` |
| Public front door | `README.md` |
| Volatile development state | this page, roadmap, task packet, runbooks, and audit evidence |
| Product truth | accepted contracts, runtime behavior, reviewed records, and accepted architecture docs |
| License | restricted source-available; not open-source |

## Implemented Or Present

| Area | Status |
| --- | --- |
| Python reference backend | Active executable lane |
| Local product loop | Present for local/operator work |
| Workbench/operator loop | Local cockpit foundation present |
| CLI/local web/local HTTP API | Present as local surfaces |
| Live search provider contract | Provider-neutral contract and Brave adapter present |
| Local `--live` search display | Experimental, bounded, operator opt-in, local only |
| Synthetic behavior cleanup | Normal search no longer silently substitutes hard-query fixtures; demo bootstrap is explicit |
| Public-alpha routes | Read-only foundations present but not the current priority |
| Snapshot/relay | Read-only snapshot-backed foundation present |
| Test/eval discipline | Focused lanes plus full-discovery harness/CI posture |

## Gated, Blocked, Or Deferred

| Area | Current gate |
| --- | --- |
| Human acceptance | Blocked until all six live Search/Hunt milestones pass |
| Safe page fetching | Incomplete; must enforce DNS, redirect, SSRF, robots, MIME, size, timeout, and concurrency policy |
| Durable live indexing | Incomplete; must persist independently fetched SourceObservations, not provider Search Results |
| Real Hunt | Incomplete; current live Hunt is query expansion/provider search only |
| Local provider calls | Allowed only through explicit local `--live` modes with operator credentials and budgets |
| Public live fanout | Disabled |
| Public alpha launch | Frozen; requires explicit manual approval and current validation evidence after the local product works |
| Public deploy dry run | Deferred; not a launch claim |
| Public open-internet exposure | Disabled; requires separate hosting, safety, rollback, and operator evidence |
| Downloads/uploads/executable actions | Disabled or future-gated |
| Broad extraction | Disabled except safe fixture/member-manifest foundations |
| Model/provider model calls | Disabled |
| Native app distribution | Not ready; native work remains a later lane |
| Rust backend replacement | Not ready; Python remains the oracle |

## Current Non-Claims

Eureka does not currently claim:

- deployed public service
- public launch
- production readiness
- completed live Search/Hunt product
- safe broad web crawling
- durable indexing of live web discoveries
- full Archive.org search
- broad corpus coverage
- rights clearance or malware safety
- download, install, execute, upload, app-store, or marketplace behavior
- native client readiness
- live public source fanout
- AI authority or autonomous truth acceptance
- open-source licensing

## Validation Posture

Use focused lanes during normal development:

```powershell
python scripts/eureka_test_select.py --changed --failed-first --json
python scripts/check_architecture_boundaries.py
```

Use live-search focused checks when touching the current product slice:

```powershell
python -m unittest tests.runtime.test_live_web_search_provider -v
python -m unittest tests.runtime.test_live_search_service -v
python -m unittest tests.e2e.test_portable_eureka_instance -v
python -m unittest tests.e2e.test_local_search_cli -v
```

Use public-alpha checks only when touching public-alpha posture:

```powershell
python scripts/validate_public_alpha_readonly.py
python scripts/validate_public_alpha_hosting_readiness.py
python scripts/validate_public_alpha_launch_candidate.py
```

Full unittest discovery is a promotion/nightly/manual lane and should run
through the harness or CI with compact summaries:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```

## Status Pointers

- [Bootstrap Status](BOOTSTRAP_STATUS.md)
- [Roadmap](ROADMAP.md)
- [Test and Eval Lanes](operations/TEST_AND_EVAL_LANES.md)
- [Architecture](ARCHITECTURE.md)
- [Open Questions](OPEN_QUESTIONS.md)
