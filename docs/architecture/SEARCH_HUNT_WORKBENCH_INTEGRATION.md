# Search Hunt Workbench Integration

HUNT-08 proves the local Search Hunt loop through the Local Appliance workbench, JSON API, and CLI.

The integrated deterministic path is:

1. Reviewed local index search creates a Search Hunt Session.
2. Operator-gated commands and steering record local intent.
3. A deterministic exhaustion report explains checked and deferred layers.
4. A SearchNeed records unresolved local demand.
5. A WorkUnit plan creates queued or policy-blocked local queue records.
6. The background hunt runner executes only safe deterministic local workers.
7. Workbench and API pages expose updated hunt, need, WorkUnit, and runner state.

The workflow does not execute source probes, extraction, AI/model providers, downloads, installs, deployment, site generation, or master-index mutation.
