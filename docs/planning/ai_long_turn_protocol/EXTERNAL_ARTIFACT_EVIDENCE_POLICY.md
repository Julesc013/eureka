# External Artifact Evidence Policy

Artifact evidence collection is external or manual when the repo has reached a
no-call boundary. AI sessions must not fabricate observations, downloads,
source probes, reviewed records, verified artifacts, rights clearance, malware
safety, or acquisition readiness.

## Current Waiting State

At creation of this protocol, the current queue state was:

```text
WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE
```

The secondary blocker was:

```text
WAITING_FOR_USER_HARDWARE_DETAILS
```

## Return Contract

The active return contract is:

```text
docs/reference/artifact_evidence_collection_handoff_00/return_contract.md
```

Expected compact return file:

```text
../eureka-evidence-runs/artifact_evidence_collection_00/artifact_evidence_collection_summary.json
```

Required top-level fields:

```text
schema_version
run_id
collected_at
collector
target_results
raw_artifacts_retained_outside_repo
downloads_performed
executables_fetched
install_or_execution_performed
rights_clearance_claimed
malware_safety_claimed
resume_recommended_task
```

Allowed target statuses:

```text
evidence_collected
partially_collected
blocked
not_found
deferred
```

## Resume Rule

After a valid compact return exists, resume at:

```text
MANUAL-ARTIFACT-OBSERVATION-BATCH-03
```

Do not jump directly to reviewed artifact corpus updates, public alpha
readiness, verified artifact claims, or `dev -> main` promotion.

## Prohibited Claims

The following are prohibited unless a future reviewed policy and evidence
explicitly support them:

- artifact verified;
- rights cleared;
- malware safe;
- compatible with a user machine;
- safe to download, install, or execute;
- source truth accepted;
- public/master index ready;
- public alpha ready.

## User Hardware Details

The Windows 98 driver recommendation remains blocked until the user supplies
device identity details such as vendor, model, chipset, bus/device id, machine
or board model, exact Windows 98 variant, and source/media context.
