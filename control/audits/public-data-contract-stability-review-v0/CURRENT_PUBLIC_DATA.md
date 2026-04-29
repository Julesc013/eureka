# Current Public Data

Generated Public Data Summaries v0 currently emits deterministic static JSON
under `public_site/data/` and matching validation copies under `site/dist/data/`.
The generator is `scripts/generate_public_data_summaries.py`.

The current files are:

| File | Current role | Current contract status |
| --- | --- | --- |
| `site_manifest.json` | High-level static publication, policy, surface, snapshot, relay, action, privacy, and host-readiness summary. | Implemented static summary, not a live API. |
| `page_registry.json` | Machine-readable projection of governed public page and reserved-route inventory. | Implemented static route/page summary. |
| `source_summary.json` | Public projection of governed source inventory posture and coverage. | Implemented static source summary. |
| `eval_summary.json` | Public projection of local archive eval, search-usefulness, and manual-baseline pending status. | Implemented static audit summary. |
| `route_summary.json` | Public-alpha route posture summary from route inventory. | Implemented static route-posture summary. |
| `build_manifest.json` | Static build/provenance and disabled-behavior summary. | Implemented diagnostic build summary. |

None of these files contain live backend output, live probe output, automated
external observations, deployment proof, private paths, secrets, account data,
telemetry, executable downloads, installer automation, malware-safety claims,
or rights-clearance claims.

The file-level contract previously used `stable_draft` for generated public
data files. This review keeps that file-level posture but narrows the promise:
only the fields listed as `stable_draft` in this pack are safe for cautious
pre-alpha client dependence. Other fields are display-only, diagnostic,
internal, future, or volatile.
