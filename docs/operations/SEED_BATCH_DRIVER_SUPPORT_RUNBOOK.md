# Driver Support Seed Batch Runbook

Use the fixture lane for normal task validation:

```bash
python scripts/eureka_seed_batch_driver_support.py --fixture --json
python scripts/eureka_seed_batch_driver_support.py --fixture --write-examples --write-inventory --json
python scripts/eureka_seed_batch_report.py --from-examples --domain driver_support_media --json
python scripts/validate_seed_batch_driver_support.py
```

Allowed source families are `internet_archive_metadata`,
`wayback_cdx_metadata`, `manual_source_pack`, `vendor_support_url_metadata`,
and `github_releases_metadata`. Non-Internet Archive families are fixture or
descriptor lanes unless future policy explicitly allows more.

Do not download packages, fetch files, extract, install, execute, run OCR,
call model providers, mutate public indexes, commit raw live responses, or
claim driver safety, compatibility, rights clearance, deployment readiness, or
public launch readiness.
