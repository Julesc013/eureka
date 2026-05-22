# Reviewed Index Policy

Policy file: `control/policies/ia_reviewed_index_policy.json`.

IA-07 enables reviewed local index rebuild only for explicit temp/local
instances. It forbids operator instance mutation, committed `site/dist/data/public_index`
mutation, master index mutation, hosted public search mutation, downloads,
uploads, extraction, model/provider calls, deployment, and production/public
launch claims.
