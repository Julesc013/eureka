# External Baseline Status

External baseline status command:

```text
python scripts/report_external_baseline_status.py --json
```

Global slot counts:

| Status | Count |
| --- | ---: |
| observed | 0 |
| pending_manual_observation | 192 |

Pending by system:

| System | Pending |
| --- | ---: |
| google_web_search | 64 |
| internet_archive_metadata_search | 64 |
| internet_archive_full_text_search | 64 |

Batch 0:

- selected query count: 13
- selected system count: 3
- observation count: 39
- observed observation count: 0
- pending observation count: 39
- completion percent: 0.0

Source Expansion v2 and Delta v2 did not create external observations. No automated external lookup, URL fetch, scrape, browser automation, Google query, Internet Archive query, Software Heritage query, SourceForge query, GitHub API call, or package registry call was performed.

