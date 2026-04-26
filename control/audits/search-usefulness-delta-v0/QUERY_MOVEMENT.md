# Query Movement

## Baseline Caveat

No committed per-query historical report exists for the baseline. This file
therefore separates:

- machine-observed current query status
- inferred movement from current output and known milestone effects
- unchanged broad family blockers

Per-query movement should be treated as directional until a future recurring
baseline report exists.

## Inferred Improved Queries

| Query ID | Current status | Movement note |
| --- | --- | --- |
| `windows_xp_software` | partial | Current recorded fixture/search output now supports a partial old-platform software answer. |
| `latest_firefox_before_xp_support_ended` | partial | Current fixture-backed evidence and planner interpretation support partial latest-compatible investigation. |
| `driver_inf_inside_support_cd` | partial | Member-level fixture records make an inner support-media member visible. |
| `support_cd_member_driver` | partial | Synthetic member records, parent lineage, and compatibility/member evidence now support a partial answer. |

## Still Blocked By Source Coverage

Representative query IDs:

- `windows_7_apps`
- `windows_7_portable_apps_archive`
- `windows_98_registry_repair`
- `windows_2000_antivirus`
- `mac_os_9_browser`
- `powerpc_osx_104_browser`
- `creative_ct1740_driver_windows_98`
- `sound_blaster_live_ct4830_driver_windows_98`
- `ati_rage_128_windows_98_driver`
- `threecom_3c905_windows_95_driver`
- `epson_scanner_windows_2000_driver`
- `directx_90c_offline_installer_windows_98`
- `visual_cpp_6_service_pack_download`

## Still Blocked By Compatibility Evidence

Representative query families:

- latest-compatible browser/software
- old-platform utilities
- driver/hardware/OS queries
- Windows 98/95 and Windows 2000 software queries

Compatibility Evidence Pack v0 makes evidence visible where current fixtures
support it, but many query families lack recorded release notes, readmes,
manuals, package metadata, or source-native platform fields.

## Still Blocked By Member/Decomposition Support

Representative query IDs:

- `readme_inside_old_zip`
- `installer_inside_iso`
- article-inside-scan queries
- support-media queries outside the bounded local ZIP fixtures

Member-Level Synthetic Records v0 helps committed local bundles. It does not
add broad ISO, OCR, WARC/WACZ, package, or scan extraction.

## Still Blocked By Planner/Query Interpretation

Planner output improved for old-platform intent, but current failure-mode
counts still include:

- `planner_gap`: 24
- `query_interpretation_gap`: 21

Remaining planner work should be driven by recorded source evidence and hard
query expectations, not by fuzzy or LLM planning.

## Not Yet Evaluable Or Externally Pending

All Google and Internet Archive external baselines remain
`pending_manual_observation`. That does not mean those systems failed; it means
this repo did not record human-reviewed observations for this audit pack.
