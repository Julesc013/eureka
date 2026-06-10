# Gap Retarget Report

## Inputs

| Input | Evidence |
|---|---|
| human artifact review batch | `HUMAN-ARTIFACT-REVIEW-BATCH-01` reviewed 6 items, promoted 2, requested more evidence for 3, and marked 1 near miss |
| artifact gate | `REVIEWED-ARTIFACT-RECORD-GATE-02` reports 4 reviewed artifact records, 0 verified artifacts, and a 21-record gap |
| full discovery | `SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-04` records rerun 04 as green for the validated pre-ingest run head |

## Retargeted Evidence Gaps

| Gap | Priority | Query | Needed Next |
|---|---|---|---|
| `gap_b02_ct1740_exact_manual_fit` | P0 | `hq_sound_blaster_ct1740_manual` | exact CT1740 fit, manual edition, page or scope evidence |
| `gap_b02_blue_ftp_visual_identity` | P0 | `hq_blue_ftp_client_xp` | blue visual identity evidence and exact XP-era package or version |
| `gap_b02_firefox_5290_exact_variant_hash` | P0 | `hq_firefox_last_xp` | exact Firefox 52.9.0esr Windows package variant and checksum reference |
| `gap_b02_firefox_115_exact_variant_hash` | P1 | `hq_windows_7_apps` | exact Firefox 115 ESR Windows variant and checksum reference |
| `gap_b02_7zip_2601_integrity_evidence` | P1 | `hq_windows_7_apps` | package integrity evidence for reviewed 7-Zip 26.01 identity |
| `gap_b02_parallel_course_primary_scan_page_range` | P1 | `hq_ray_tracing_1994_magazine` | primary issue, scan, page range, or authoritative page-scope evidence |

The Windows 98 driver query remains outside this collection batch until user hardware details are available.
