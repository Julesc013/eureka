# Action Manifest Contract

`contracts/command/actions/action_manifest.v0.json` describes a non-executing action envelope.

An action manifest may describe a metadata view, local inspection, comparison, citation, export manifest, preservation manifest, acquisition manifest, or a blocked action report.

It must preserve these current boundaries:

- `action_manifest_executes_action: false`
- `action_manifest_downloads_file: false`
- `action_manifest_installs_artifact: false`
- `action_manifest_runs_artifact: false`
- `action_manifest_mutates_public_index: false`
- `action_manifest_mutates_master_index: false`

Risky actions produce blocked reports only. A manifest is not evidence acceptance, candidate acceptance, rights clearance, malware safety, installability verification, or compatibility certification.
