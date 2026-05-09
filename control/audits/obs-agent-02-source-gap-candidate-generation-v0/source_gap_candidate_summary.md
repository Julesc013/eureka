# Source Gap Candidate Summary

OBS-AGENT-02 generated review-gated source gap candidates from committed repo-local materials only.

## Source Families Recommended For Review

| Priority | Candidate | Source family | Source mode | Review action |
| --- | --- | --- | --- | --- |
| 82 | `obs_candidate_source_gap_internet_archive_metadata_v0` | `internet_archive_metadata` | `approved_metadata_probe_future` | Prepare a human source policy decision packet for metadata-only Internet Archive access before any automated request is considered. |
| 76 | `obs_candidate_source_gap_wayback_metadata_v0` | `wayback_cdx_memento_metadata` | `approved_metadata_probe_future` | Prepare a source policy decision packet for availability and capture metadata only, including URI privacy and forbidden content retrieval constraints. |
| 70 | `obs_candidate_source_gap_github_releases_v0` | `github_releases_metadata` | `approved_api_future` | Prepare a source policy decision packet for repository identity-reviewed release metadata only. |
| 66 | `obs_candidate_source_gap_package_registry_v0` | `package_registry_metadata` | `approved_api_future` | Prepare source policy decisions for metadata-only PyPI and npm-style registry access, including package identity and scoped package review. |
| 46 | `obs_candidate_source_gap_manual_only_forum_v0` | `manual_only_forum_or_community` | `manual_human_only` | Keep community or forum leads manual-only until a human source decision defines permissions, quoting rules, and evidence limits. |
| 24 | `obs_candidate_source_gap_policy_blocked_v0` | `broad_web_policy_blocked` | `no_autonomous_access` | Keep this as a blocked policy decision item unless a future approved API and source policy packet exists. |

## Local Evidence

- `obs_candidate_source_gap_internet_archive_metadata_v0`: Repo-local source inventory and eval materials indicate that Internet Archive-style item metadata could help old-platform, archived software, file-listing, and member-discovery gaps after source policy review.
  Evidence refs: `control/inventory/sources/internet-archive-placeholder.source.json`, `control/inventory/sources/internet-archive-recorded-fixtures.source.json`, `evals/search_usefulness/external_baselines/systems.json`, `control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json`
- `obs_candidate_source_gap_wayback_metadata_v0`: Repo-local source inventory shows Wayback/Memento as a deferred metadata source family for dead vendor pages, release notes, and temporal capture gaps.
  Evidence refs: `control/inventory/sources/wayback-memento-placeholder.source.json`, `control/inventory/sources/wayback-memento-recorded-fixtures.source.json`, `docs/reference/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.md`, `evals/search_usefulness/external_baselines/systems.json`
- `obs_candidate_source_gap_github_releases_v0`: Repo-local GitHub Releases fixtures and approval packs indicate that release metadata could address version, source identity, and representation gaps after policy review.
  Evidence refs: `control/inventory/sources/github-releases-recorded-fixtures.source.json`, `control/audits/github-releases-connector-approval-v0/`, `docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`
- `obs_candidate_source_gap_package_registry_v0`: Repo-local package registry fixtures and approval packs indicate that package/version metadata could address package identity, source archive, and release metadata gaps after policy review.
  Evidence refs: `control/inventory/sources/package-registry-recorded-fixtures.source.json`, `control/audits/pypi-metadata-connector-approval-v0/`, `control/audits/npm-metadata-connector-approval-v0/`, `docs/operations/NPM_METADATA_CONNECTOR_RUNTIME_PLAN.md`
- `obs_candidate_source_gap_manual_only_forum_v0`: Repo-local eval and recorded review-description fixtures indicate that community descriptions may help vague identity and compatibility questions, but they remain manual-only or permission-needed review items.
  Evidence refs: `control/inventory/sources/review-description-recorded-fixtures.source.json`, `evals/search_usefulness/queries/search_usefulness_v0.json`, `docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md`
- `obs_candidate_source_gap_policy_blocked_v0`: Repo-local baseline system policy identifies broad web search as a useful recall comparison for humans, but autonomous result-page access remains blocked.
  Evidence refs: `evals/search_usefulness/external_baselines/systems.json`, `docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md`, `control/inventory/observations/observation_source_access_modes.json`

## Uncertain

- Source fit is inferred from committed local inventories, audits, docs, eval query classes, and candidate examples.
- No candidate is an observed baseline, accepted evidence, source approval, connector runtime, or master-index mutation.
- Future Track B consumption depends on matching contracts and review gates.

## Source Policy Decisions Needed

- Internet Archive metadata policy.
- Wayback/CDX/Memento availability and capture metadata policy.
- GitHub Releases metadata policy.
- PyPI/npm-style package metadata policy.
- Manual-only community or forum lead policy.
- Broad web recall baseline policy for any future approved API path.

## Likely Future Seeds

- SearchNeed seeds: Internet Archive, Wayback/CDX/Memento, GitHub Releases, and package registry metadata candidates.
- WorkUnit seeds: source policy review packets for each candidate family.
- Connector pattern candidates: metadata-only Internet Archive is the strongest first review target because it has high local relevance and a bounded metadata shape.

## Policy-Blocked

- `obs_candidate_source_gap_policy_blocked_v0` remains blocked for autonomous source access.
