# Source Policy Decision Queue Preview

This preview is not source approval. It lists future human/operator decisions suggested by OBS-AGENT-02 source gap candidates.

## Decision Items

| Priority | Source family | Candidate | Needed decision |
| --- | --- | --- | --- |
| 82 | Internet Archive metadata | `obs_candidate_source_gap_internet_archive_metadata_v0` | Decide whether metadata-only item/search/file-list access can be scoped, cached, attributed, rate-limited, and reviewed later. |
| 76 | Wayback/CDX/Memento metadata | `obs_candidate_source_gap_wayback_metadata_v0` | Decide whether availability and capture metadata can be scoped without archived content retrieval or arbitrary URL fanout. |
| 70 | GitHub Releases metadata | `obs_candidate_source_gap_github_releases_v0` | Decide whether repository identity-reviewed release metadata can be accessed later without clones, raw file fetches, archive retrieval, or asset downloads. |
| 66 | Package registry metadata | `obs_candidate_source_gap_package_registry_v0` | Decide whether PyPI/npm-style metadata can be accessed later without installs, dependency resolution, lifecycle execution, package retrieval, or package archive inspection. |
| 46 | Manual-only community/forum leads | `obs_candidate_source_gap_manual_only_forum_v0` | Decide whether manual-only paraphrased community descriptions are allowed, what permissions apply, and how subjective evidence is bounded. |
| 24 | Broad web policy-blocked baseline | `obs_candidate_source_gap_policy_blocked_v0` | Keep blocked unless a future approved API and source policy packet exists. |

## Required Review Inputs

- Source family scope.
- Allowed endpoint, API, page, or fixture surface.
- Forbidden endpoint, page, artifact, account, upload, download, and execution surfaces.
- Rate limit, timeout, retry, and kill switch.
- Terms, robots, privacy, and rights-risk posture.
- Cache and evidence destination.
- Output contract and review requirement.

## Boundary

No item in this queue preview authorizes source access, source sync, live probes, connector runtime, public search fanout, evidence truth, or master-index mutation.
