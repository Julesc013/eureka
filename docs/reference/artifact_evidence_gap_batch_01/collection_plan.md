# Collection Plan

Collection mode:

```text
manual_reference_packet_only
```

Allowed:

- create manual reference packets from already bounded source-reference work
- record bibliographic, version, checksum-index, page-scope, and identity evidence
- carry non-promoted leads as needs or near misses

Not allowed:

- runtime source calls
- scraping or crawling
- downloads or binary fetches
- Wayback replay
- installs, execution, extraction, emulation, or malware assessment
- source observation self-promotion
- reviewed/public/master index mutation

## Next Manual Batch Targets

| Target | Source Family | Desired Evidence |
|---|---|---|
| `target_b02_ct1740_manual_fit` | publisher manual catalog or reputable manual index | exact CT1740 model fit, manual title, edition, and page or scope evidence |
| `target_b02_blue_ftp_visual_identity` | vendor docs, screenshot reference, review page, or archived UI reference already eligible for manual packet work | blue UI evidence, product/version identity, XP-era support context |
| `target_b02_firefox_5290_hash` | publisher release metadata or checksum reference | exact Windows package variant, checksum reference, signature reference if available without binary fetch |
| `target_b02_firefox_115_hash` | publisher release metadata or checksum reference | exact Windows package variant, checksum reference, signature reference if available without binary fetch |
| `target_b02_7zip_2601_integrity` | official project release metadata or checksum reference | package identity, checksum or signature reference, integrity-source context |
| `target_b02_parallel_course_page_scope` | publisher catalog, issue index, author bibliography, or primary scan index | issue identity, page range, article title, author, rights-risk note |

The next task should create the manual reference packets and leave review decisions to a later human artifact review batch.
