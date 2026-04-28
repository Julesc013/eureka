# Milestone Status

| Milestone | Status | Evidence | Validation |
| --- | --- | --- | --- |
| Public Publication Plane Contracts v0 | implemented | `control/inventory/publication/` | `python scripts/validate_publication_inventory.py` |
| GitHub Pages Deployment Enablement v0 | implemented | `.github/workflows/pages.yml` | `python scripts/check_github_pages_static_artifact.py` |
| Static Site Generation Migration v0 | implemented | `site/build.py` | `python site/build.py --check` |
| Generated Public Data Summaries v0 | implemented | `public_site/data/site_manifest.json` | `python scripts/generate_public_data_summaries.py --check` |
| Lite/Text/Files Seed Surfaces v0 | implemented | `public_site/lite/` | `python scripts/generate_compatibility_surfaces.py --check` |
| Static Resolver Demo Snapshots v0 | implemented | `public_site/demo/` | `python scripts/generate_static_resolver_demos.py --check` |
| Custom Domain / Alternate Host Readiness v0 | implemented | `control/inventory/publication/domain_plan.json` | `python scripts/validate_static_host_readiness.py` |
| Live Backend Handoff Contract v0 | implemented | `control/inventory/publication/live_backend_handoff.json` | `python scripts/validate_live_backend_handoff.py` |
| Live Probe Gateway Contract v0 | implemented | `control/inventory/publication/live_probe_gateway.json` | `python scripts/validate_live_probe_gateway.py` |
| Rust Query Planner Parity Candidate v0 | implemented; optional Cargo unavailable | `crates/eureka-core/src/query_planner.rs` | `python scripts/check_rust_query_planner_parity.py` |
| Compatibility Surface Strategy v0 | implemented | `docs/architecture/COMPATIBILITY_SURFACES.md` | `python scripts/validate_compatibility_surfaces.py` |
| Signed Snapshot Format v0 | implemented | `snapshots/examples/static_snapshot_v0/` | `python scripts/validate_static_snapshot.py` |

No queued P01-P09 milestone is missing by file evidence in this checkpoint. Rust Cargo execution remains environment-unavailable, so Rust compile/test evidence is not claimed here.
