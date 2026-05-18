# IA-06 Review Promotion Dry-Run Audit

IA-06 adds a local review queue and promotion dry-run lane for Internet
Archive metadata candidate records.

The audit proves:

- IA candidates can be loaded into a review queue in a temp explicit instance.
- Local review decisions can be recorded.
- Approval decisions create promotion previews only.
- Reviewed and master indexes remain untouched.
- No accepted truth, raw response, download, upload, extraction, provider call,
  deployment, or production/public launch claim is created.

