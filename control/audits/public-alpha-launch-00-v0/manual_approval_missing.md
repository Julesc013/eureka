# Manual Approval Missing

`PUBLIC-ALPHA-LAUNCH-00` stopped before any launch-affecting action because no
manual approval record was found.

Checked locations:

- `control/approvals/public-alpha-launch-00-approval.json`: missing
- `control/inventory/public_alpha_launch_manual_approval.json`: missing

Required approval fields:

- `schema_version`
- `task`: `PUBLIC-ALPHA-LAUNCH-00`
- `approved_by`
- `approved_at`
- `approval_phrase`: `LAUNCH_READ_ONLY_PUBLIC_ALPHA`
- `target_environment`
- `deployment_mode`
- `domain_or_url`
- `deployment_command`
- `rollback_command`
- `rollback_contact`
- `acknowledged_boundaries`

Required acknowledged boundaries:

- `read_only`
- `no_public_mutation`
- `no_live_source_fanout`
- `no_downloads`
- `no_extraction`
- `no_model_provider_calls`
- `alpha_limited_corpus`
- `manual_rollback_required`

No deployment, publishing, DNS change, hosting provider call, live source call,
download, extraction, model/provider call, public mutation, or public live source
fanout occurred.
