# Hard Query Set Report

Task ID: `HARD-QUERY-EVAL-00`

## Registry

Path:

```text
evals/hard_queries/hard_query_set_v0.json
```

## Required Queries

| Query ID | Query Text | Intent Type |
|---|---|---|
| `hq_windows_7_apps` | `Windows 7 apps` | `software_discovery` |
| `hq_driver_win98` | `driver for Win98` | `driver_discovery` |
| `hq_blue_ftp_client_xp` | `old blue FTP client for XP` | `artifact_identification` |
| `hq_sound_blaster_ct1740_manual` | `manual for Sound Blaster CT1740` | `manual_documentation` |
| `hq_firefox_last_xp` | `latest Firefox before XP support ended` | `version_history` |
| `hq_ray_tracing_1994_magazine` | `article about ray tracing in a 1994 magazine` | `periodical_article_discovery` |

## Required Fields

Each query defines:

```text
query_id
query_text
intent_summary
intent_type
object_types_expected
smallest_useful_unit
allowed_result_statuses
minimum_useful_public_output
expected_evidence_shape
known_ambiguities
near_miss_rules
absence_rules
policy_block_rules
allowed_source_families_for_future_runs
forbidden_actions
renderer_profiles_required
score_weights
public_alpha_relevance
notes
```

## Scope

The query set is a usefulness eval registry only. It is not reviewed evidence and does not claim corpus coverage.
