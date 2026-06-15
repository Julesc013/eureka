# Artifact Evidence Source Collection

This runbook covers `ARTIFACT-EVIDENCE-SOURCE-COLLECTION-00`: the first bounded
source-observation bridge into the reviewed-artifact gate workflow.

It does not crawl the web, download binaries, fetch files, replay Wayback,
promote fixture or IA metadata into verified artifact truth, complete the
25-record gate by itself, deploy, or launch public alpha.

## Prerequisites

Start from a valid reviewed-artifact seed and manual evidence batch:

```powershell
python scripts/eureka_artifact_gate.py validate --gate .eureka/artifact-gate/public-alpha-seed

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

If either artifact is missing, run:

- `docs/runbooks/REVIEWED_ARTIFACT_GATE_SEED.md`
- `docs/runbooks/MANUAL_ARTIFACT_EVIDENCE_BATCH.md`

Generated `.eureka` files are local ignored artifacts. Do not commit them.

## Source Plan

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-collection-01 --target-records 5
```

This writes:

```text
.eureka/artifact-gate/source-collection-01/collection_manifest.json
.eureka/artifact-gate/source-collection-01/source_candidate_plan.jsonl
.eureka/artifact-gate/source-collection-01/source_url_list_template.jsonl
```

The plan prefers concrete manual-batch candidates. Broad `Windows 7 apps`,
under-specified `driver for Win98`, unavailable records, and policy-blocked
records remain excluded until they become specific, safe artifact identities.

## Source Observation Template

```powershell
python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-collection-01 --out .eureka/artifact-gate/source-collection-01/source_observation_template.jsonl
```

Fill a separate `source_observations.jsonl` from the template. Required fields
include:

- `source_observation_id`
- `collection_id`
- `candidate_id`
- `artifact_title`
- `artifact_type`
- `artifact_identity_fields`
- `platform_or_context`
- `source_id`
- `source_url` or `source_identifier`
- `source_type`
- `source_authority`
- `observed_artifact_fields`
- `short_evidence_summary`
- `access_method`
- `observed_at` or `collected_at`
- `observer`
- `no_download_performed=true`
- `downloaded_file=false`
- `fetched_binary=false`
- `file_fetch_performed=false`
- `wayback_replay_used=false`
- `proposed_verification_scope`
- `proposed_artifact_verified`
- `proposed_gate_eligible`
- `limitations`

Keep excerpts short. Prefer field extraction and paraphrase over quotation.

## Acceptable Source Types

Useful source observations can come from:

- official support pages;
- official release notes;
- manual pages;
- stable catalog pages;
- archive metadata pages as source leads;
- publication records;
- reputable secondary references.

`artifact_verified=true` should be proposed only for explicit artifact identity
evidence, such as primary/official source metadata, or a stable archive/catalog
source with independent reputable corroboration.

## Unacceptable Source Types

These may be source leads, but must not verify artifacts by themselves:

- local fixtures;
- IA metadata alone;
- local demo reviewed records;
- broad category pages;
- unknown authority pages;
- source hints with no observer and rationale;
- private local paths;
- files, binaries, downloads, Wayback replay, installers, emulators, or
  marketplace actions.

Source observation does not imply `binary_verified`, `download_safe`,
`execution_safe`, `rights_cleared`, or malware safety. Those fields stay false
unless a separate approved process proves them.

## Ingest And Validate

When source observations are available:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-collection-01 --observations .eureka/artifact-gate/source-collection-01/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-collection-01
```

If `source_observations.jsonl` is absent, validation reports a blocked warning
and creates no evidence packets.

Validation rejects missing observer, missing source identifier, missing observed
fields, downloaded files, fetched binaries, Wayback replay, local fixture
verified claims, IA-metadata-only verified claims, broad records, and driver
records without hardware details.

## Convert To Manual Evidence

```powershell
python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-collection-01 --out .eureka/artifact-gate/source-collection-01/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-collection-01 --out .eureka/artifact-gate/source-collection-01/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-collection-01
```

The collection writes:

```text
.eureka/artifact-gate/source-collection-01/source_observations.jsonl
.eureka/artifact-gate/source-collection-01/source_validation_report.json
.eureka/artifact-gate/source-collection-01/manual_evidence_packets.jsonl
.eureka/artifact-gate/source-collection-01/source_collection_report.json
.eureka/artifact-gate/source-collection-01/SOURCE_COLLECTION_REPORT.md
```

Valid non-verified observations become manual evidence packets with
`artifact_verified=false` and `gate_eligible=false`. Only observations that pass
the explicit criteria can produce `artifact_verified=true`.

## Feed Manual Batch

Use source-derived packets as input to the existing manual batch:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-collection-01/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_collection_01 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Manual review materializes only valid, artifact-verified, gate-eligible packets.
Below 25 reviewed artifacts, the gate remains blocked.

## Launch Gate

```powershell
python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --corpus-gate-closeout .eureka/corpus-gate/public-alpha/latest/corpus_gate_closeout.json --out .eureka/launch/public-alpha/latest

python scripts/eureka_public_alpha_launch_gate.py validate-report --report .eureka/launch/public-alpha/latest/launch_gate_report.json

python scripts/eureka_public_alpha_launch_gate.py status --report .eureka/launch/public-alpha/latest/launch_gate_report.json
```

The launch gate consumes the updated manual batch report and, after Batch 09,
the public-alpha corpus gate closeout. Use
`docs/runbooks/PUBLIC_ALPHA_CORPUS_GATE_CLOSEOUT.md` to create that closeout
and rebuild staging. Launch must remain blocked unless deployment, release,
approval, and safety gates are genuinely satisfied.

## Expected No-Observation Result

If no source observations are supplied, expect `PASS_WITH_WARNINGS`:

```text
valid_observation_count=0
evidence_packet_count=0
artifact_verified_packet_count=0
reviewed_artifact_gate_count=0/25
launch_status=BLOCKED
```

This is a useful handoff state, not a failure.

## Source Observation Batch 01

`SOURCE-OBSERVATION-BATCH-01` is the first bounded batch that adds real page
observations to the source collection path. It keeps the same no-download,
no-file-fetch, no-Wayback, no-launch posture.

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-01 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-01 --out .eureka/artifact-gate/source-observation-batch-01/source_observation_template.jsonl
```

Fill these generated files:

```text
.eureka/artifact-gate/source-observation-batch-01/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-01/source_observations.jsonl
```

Batch 01 observes at most three pages:

- Firefox ESR 52.9.0 system requirements, as an official support page.
- Firefox ESR 52.9.0 release notes, as official release notes.
- Phil's Computer Lab CT1740 page, as a reputable secondary source lead.

The Firefox observations can propose `artifact_verified=true` for artifact
identity metadata only. The CT1740 observation remains
`artifact_verified=false` because it is a secondary hardware source lead, not a
verified manual artifact. None of these observations imply binary, download,
execution, rights, or malware safety.

Run the batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-01 --observations .eureka/artifact-gate/source-observation-batch-01/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-01 --out .eureka/artifact-gate/source-observation-batch-01/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-01 --out .eureka/artifact-gate/source-observation-batch-01/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01
```

Feed the generated manual packets into the manual batch:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-01/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_01 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Expected current Batch 01 result:

```text
source observations: 3 valid / 0 invalid
source evidence packets: 2
artifact verified packets: 1
reviewed artifact gate count: 1/25
launch status: BLOCKED
```

This closes the first real observation loop, but it does not complete the
reviewed-artifact gate or authorize public launch. Continue with another
source-observation batch when more artifact evidence is needed.

## Source Observation Batch 02

`SOURCE-OBSERVATION-BATCH-02` extends the same lane with a new bounded source
observation batch. It preserves Batch 01 evidence, avoids re-counting Firefox
ESR 52.9.0, and adds one corroborated Sound Blaster manual identity packet.

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-02 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-02 --out .eureka/artifact-gate/source-observation-batch-02/source_observation_template.jsonl
```

Fill these generated files:

```text
.eureka/artifact-gate/source-observation-batch-02/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-02/source_observations.jsonl
```

Batch 02 records bounded page/catalog observations for the Sound Blaster manual
candidate:

- Internet Archive metadata for `Creative Labs Sound Blaster 16 manual`, as an
  archive metadata source lead.
- A stable catalog record for `Sound Blaster 16 User's Guide`, as independent
  corroborating artifact identity metadata.
- DOSDays CT1740 hardware context, as a reputable secondary platform/context
  source lead.

Archive metadata alone must remain `artifact_verified=false`. The verified
Batch 02 packet is allowed only because the archive/source lead is corroborated
by independent catalog metadata and hardware context. None of these observations
imply binary, download, execution, rights, marketplace, or malware safety.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-02 --observations .eureka/artifact-gate/source-observation-batch-02/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-02 --out .eureka/artifact-gate/source-observation-batch-02/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-02 --out .eureka/artifact-gate/source-observation-batch-02/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02
```

Preserve Batch 01 when feeding Batch 02 into the active manual batch. Because
`manual-ingest` replaces the active manual evidence file with the supplied file,
build a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual gate:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-02/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_02 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Expected current Batch 02 result:

```text
source observations: 3 valid / 0 invalid
source evidence packets: 1
artifact verified packets: 1
cumulative manual evidence packets: 3
reviewed artifact gate count: 2/25
launch status: BLOCKED
```

Manual review deduplicates verified artifact identities by artifact identity and
verification scope. A repeated Firefox ESR 52.9.0 evidence packet should be
reported as `duplicate_artifact_identity`, not counted as another reviewed
artifact.

## Source Observation Batch 03

`SOURCE-OBSERVATION-BATCH-03` continues bounded evidence intake and strengthens
target de-duplication. Source planning should not target already counted
Firefox ESR 52.9.0 or Sound Blaster 16 manual/User's Guide identities as new
gate records.

Prerequisite status checks:

```powershell
python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-03 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-03 --out .eureka/artifact-gate/source-observation-batch-03/source_observation_template.jsonl
```

Fill:

```text
.eureka/artifact-gate/source-observation-batch-03/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-03/source_observations.jsonl
```

Batch 03 can target the ray-tracing article need only after it is narrowed to a
concrete article identity. The current bounded target is:

```text
Mike Miller's Many Hats
IEEE Computer Graphics and Applications
Vol. 14, No. 1, January 1994, pages 4-6
DOI 10.1109/MCG.1994.10003
```

Useful source observations for this target include:

- the IEEE Computer Society publication record, as primary publication
  metadata;
- Ray Tracing News Vol. 7 No. 1, as independent ray-tracing context and
  bibliographic corroboration;
- a reputable FAQ/catalog/bibliographic source as secondary corroboration.

Do not use article PDFs, downloads, file fetches, Wayback replay, hidden
member extraction, marketplace actions, or long copied text.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-03 --observations .eureka/artifact-gate/source-observation-batch-03/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-03

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-03 --out .eureka/artifact-gate/source-observation-batch-03/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-03 --out .eureka/artifact-gate/source-observation-batch-03/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-03
```

Preserve prior batches with a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual and launch gates:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-03/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_03 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

Expected current Batch 03 result:

```text
source observations: 3 valid / 0 invalid
source evidence packets: 1
artifact verified packets: 1
cumulative manual evidence packets: 4
reviewed artifact gate count: 3/25
launch status: BLOCKED
```

Expected alternate outcomes:

- New gate-eligible artifact: manual count may increase by one unique identity.
- Corroboration-only evidence: record as `artifact_verified=false` or duplicate
  corroboration; do not increment the gate.
- No valid observations: keep the source URL list/template as a handoff and
  report `PASS_WITH_WARNINGS`.

## Source Observation Batch 04

`SOURCE-OBSERVATION-BATCH-04` continues evidence accumulation after the first
three unique reviewed identities:

```text
Firefox ESR 52.9.0
Creative Labs Sound Blaster 16 manual / User's Guide
Mike Miller's Many Hats
```

Batch 04 first checks the remaining local candidates. If those candidates are
duplicates, broad categories, unavailable records, or unsafe/under-specified
needs, source planning may add a small curated target list of concrete safe
artifact identities. Curated targets are still only source targets until
evidence is collected and reviewed.

Prerequisite status checks:

```powershell
python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-03

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-04 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-04 --out .eureka/artifact-gate/source-observation-batch-04/source_observation_template.jsonl
```

Batch 04 de-duplicates the already counted Firefox, Sound Blaster manual/User's
Guide, and Mike Miller article identities. The current curated targets are:

```text
7-Zip 19.00 for Windows
WinSCP 5.21.8
```

Fill:

```text
.eureka/artifact-gate/source-observation-batch-04/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-04/source_observations.jsonl
```

Useful page observations for these targets include:

- the official 7-Zip download page and product page;
- the official WinSCP older-version history page;
- the SourceForge WinSCP 5.21.8 file-listing page as catalog corroboration.

Observe page metadata only. Do not open direct `.exe`, `.zip`, `.7z`, `.msi`,
installer, source archive, package, or download-file links. Do not use Wayback,
hidden member extraction, install/emulation behavior, or marketplace actions.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-04 --observations .eureka/artifact-gate/source-observation-batch-04/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-04

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-04 --out .eureka/artifact-gate/source-observation-batch-04/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-04 --out .eureka/artifact-gate/source-observation-batch-04/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-04
```

Preserve prior batches with a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-04\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-04\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual and launch gates:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-04/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_04 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

Expected current Batch 04 result:

```text
source observations: 4 valid / 0 invalid
source evidence packets: 2
artifact verified packets: 2
cumulative manual evidence packets: 6
reviewed artifact gate count: 5/25
launch status: BLOCKED
```

If the curated targets become duplicates in a later batch, they must be treated
as duplicate or corroboration-only evidence and must not increment the gate.

## Source Observation Batch 05

`SOURCE-OBSERVATION-BATCH-05` continues the curated-target path after Batch 04.
It treats the earlier counted identities as duplicates:

```text
Firefox ESR 52.9.0
Creative Labs Sound Blaster 16 manual / User's Guide
Mike Miller's Many Hats
7-Zip 19.00 for Windows
WinSCP 5.21.8
```

After those identities are excluded from the next source target pass, the current
curated targets are:

```text
PuTTY 0.78 for Windows
Audacity 3.2.5 for Windows
```

Prerequisite status checks:

```powershell
python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-03

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-04

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-05 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-05 --out .eureka/artifact-gate/source-observation-batch-05/source_observation_template.jsonl
```

Fill:

```text
.eureka/artifact-gate/source-observation-batch-05/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-05/source_observations.jsonl
```

Useful page observations for these targets include:

- the official PuTTY 0.78 release page and official PuTTY change log;
- the official Audacity 3.2.5 changelog/support page;
- the official Audacity 3.2 family changelog/support page as corroboration.

Observe page metadata only. Do not open direct installer, standalone binary,
source archive, package, or download-file links. Do not use Wayback, hidden
member extraction, install/emulation behavior, marketplace actions, or any live
download/file-fetch behavior.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-05 --observations .eureka/artifact-gate/source-observation-batch-05/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-05

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-05 --out .eureka/artifact-gate/source-observation-batch-05/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-05 --out .eureka/artifact-gate/source-observation-batch-05/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-05
```

Preserve prior batches with a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-04\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-05\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-05\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual and launch gates:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-05/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_05 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

Expected current Batch 05 result:

```text
source observations: 4 valid / 0 invalid
source evidence packets: 2
artifact verified packets: 2
cumulative manual evidence packets: 8
reviewed artifact gate count: 7/25
launch status: BLOCKED
```

The Batch 05 observations can propose `artifact_verified=true` only for artifact
identity metadata. They do not imply binary verification, download safety,
execution safety, rights clearance, marketplace safety, or public launch
readiness.

## Source Observation Batch 06

`SOURCE-OBSERVATION-BATCH-06` continues the curated-target path after Batch 05.
It treats the earlier counted identities as duplicates:

```text
Firefox ESR 52.9.0
Creative Labs Sound Blaster 16 manual / User's Guide
Mike Miller's Many Hats
7-Zip 19.00 for Windows
WinSCP 5.21.8
PuTTY 0.78 for Windows
Audacity 3.2.5 for Windows
```

After those identities are excluded from the next source target pass, the
current curated targets are:

```text
VLC 3.0.20 Vetinari
GIMP 2.10.38 for Windows
```

Prerequisite status checks:

```powershell
python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-03

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-04

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-05

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-06 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-06 --out .eureka/artifact-gate/source-observation-batch-06/source_observation_template.jsonl
```

Fill:

```text
.eureka/artifact-gate/source-observation-batch-06/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-06/source_observations.jsonl
```

Useful page observations for these targets include:

- the official VideoLAN VLC 3.0.20 release page;
- the official VideoLAN VLC 3.0.x changelog/NEWS page as corroboration;
- the official VideoLAN Security Bulletin VLC 3.0.20 page as corroboration;
- the official GIMP 2.10.38 release page;
- the official GIMP downloads page as source-tarball/hash corroboration.

Observe page metadata only. Do not open direct installer, standalone binary,
source archive, package, or download-file links. Do not use Wayback, hidden
member extraction, install/emulation behavior, marketplace actions, or any live
download/file-fetch behavior.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-06 --observations .eureka/artifact-gate/source-observation-batch-06/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-06

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-06 --out .eureka/artifact-gate/source-observation-batch-06/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-06 --out .eureka/artifact-gate/source-observation-batch-06/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-06
```

Preserve prior batches with a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-04\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-05\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-06\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-06\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual and launch gates:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-06/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_06 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

Expected current Batch 06 result:

```text
source observations: 5 valid / 0 invalid
source evidence packets: 2
artifact verified packets: 2
cumulative manual evidence packets: 10
reviewed artifact gate count: 9/25
launch status: BLOCKED
```

The Batch 06 observations can propose `artifact_verified=true` only for artifact
identity metadata. They do not imply binary verification, download safety,
execution safety, rights clearance, marketplace safety, or public launch
readiness.

## Source Observation Batch 07

`SOURCE-OBSERVATION-BATCH-07` continues the curated-target path after Batch 06.
It treats the earlier counted identities as duplicates:

```text
Firefox ESR 52.9.0
Creative Labs Sound Blaster 16 manual / User's Guide
Mike Miller's Many Hats
7-Zip 19.00 for Windows
WinSCP 5.21.8
PuTTY 0.78 for Windows
Audacity 3.2.5 for Windows
VLC 3.0.20 Vetinari
GIMP 2.10.38 for Windows
```

After those identities are excluded from the next source target pass, the
current curated targets are:

```text
Notepad++ v8.6 for Windows
Inkscape 1.3.2 for Windows
LibreOffice 7.6.7 Community for Windows
Apache OpenOffice 4.1.15 for Windows
```

Prerequisite status checks:

```powershell
python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-03

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-04

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-05

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-06

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-07 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-07 --out .eureka/artifact-gate/source-observation-batch-07/source_observation_template.jsonl
```

Fill:

```text
.eureka/artifact-gate/source-observation-batch-07/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-07/source_observations.jsonl
```

Useful page observations for these targets include:

- the official Notepad++ v8.6 release page;
- the official Inkscape 1.3.2 release notes page;
- the official Inkscape 1.3 release notes page as Windows-platform
  corroboration;
- the official Document Foundation LibreOffice 7.6.7 Community announcement;
- the official Apache OpenOffice 4.1.15 announcement;
- the official Apache OpenOffice 4.1.15 release notes page as platform
  corroboration.

Observe page metadata only. Do not open direct installer, standalone binary,
source archive, package, or download-file links. Do not use Wayback, hidden
member extraction, install/emulation behavior, marketplace actions, or any live
download/file-fetch behavior.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-07 --observations .eureka/artifact-gate/source-observation-batch-07/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-07

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-07 --out .eureka/artifact-gate/source-observation-batch-07/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-07 --out .eureka/artifact-gate/source-observation-batch-07/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-07
```

Preserve prior batches with a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-04\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-05\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-06\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-07\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-07\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual and launch gates:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-07/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_07 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

Expected current Batch 07 result:

```text
source observations: 6 valid / 0 invalid
source evidence packets: 4
artifact verified packets: 4
cumulative manual evidence packets: 14
reviewed artifact gate count: 13/25
launch status: BLOCKED
```

The Batch 07 observations can propose `artifact_verified=true` only for artifact
identity metadata. They do not imply binary verification, download safety,
execution safety, rights clearance, marketplace safety, or public launch
readiness.

## Source Observation Batch 08

`SOURCE-OBSERVATION-BATCH-08` continues the curated-target path after Batch 07.
It treats the earlier counted identities as duplicates:

```text
Firefox ESR 52.9.0
Creative Labs Sound Blaster 16 manual / User's Guide
Mike Miller's Many Hats
7-Zip 19.00 for Windows
WinSCP 5.21.8
PuTTY 0.78 for Windows
Audacity 3.2.5 for Windows
VLC 3.0.20 Vetinari
GIMP 2.10.38 for Windows
Notepad++ v8.6 for Windows
Inkscape 1.3.2 for Windows
LibreOffice 7.6.7 Community for Windows
Apache OpenOffice 4.1.15 for Windows
```

After those identities are excluded from the next source target pass, Batch 08
may use a very-high-throughput target of five curated concrete artifacts:

```text
Wireshark 4.2.3 for Windows
SumatraPDF 3.5.2 for Windows
Thunderbird 115.10.1 for Windows
IrfanView 4.67 for Windows
Paint.NET 5.0.13 for Windows
```

Prerequisite status checks:

```powershell
python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-03

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-04

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-05

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-06

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-07

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-08 --target-records 5

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-08 --out .eureka/artifact-gate/source-observation-batch-08/source_observation_template.jsonl
```

Fill:

```text
.eureka/artifact-gate/source-observation-batch-08/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-08/source_observations.jsonl
```

Useful page observations for these targets include:

- the official Wireshark 4.2.3 release news page;
- the official Wireshark 4.2.3 release notes page as corroboration;
- the official SumatraPDF version history;
- the official SumatraPDF product page as Windows-context corroboration;
- the official Thunderbird 115.10.1 release notes page;
- the official IrfanView history page;
- the official IrfanView 64-bit page as Windows-context corroboration;
- the official Paint.NET roadmap/change log;
- the official Paint.NET 5.0.13 release post as corroboration.

Observe page metadata only. Do not open direct installer, standalone binary,
source archive, package, or download-file links. Do not use Wayback, hidden
member extraction, install/emulation behavior, marketplace actions, or any live
download/file-fetch behavior.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-08 --observations .eureka/artifact-gate/source-observation-batch-08/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-08

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-08 --out .eureka/artifact-gate/source-observation-batch-08/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-08 --out .eureka/artifact-gate/source-observation-batch-08/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-08
```

Preserve prior batches with a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-04\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-05\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-06\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-07\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-08\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-08\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual and launch gates:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-08/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_08 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

Expected current Batch 08 result:

```text
source observations: 9 valid / 0 invalid
source evidence packets: 5
artifact verified packets: 5
cumulative manual evidence packets: 19
reviewed artifact gate count: 18/25
launch status: BLOCKED
```

Batch 08 can contain multiple new gate-eligible artifacts, corroboration-only
observations for those same artifacts, or no valid observations if safe pages are
unavailable. The accepted observations can propose `artifact_verified=true` only
for artifact identity metadata. They do not imply binary verification, download
safety, execution safety, rights clearance, marketplace safety, or public launch
readiness.

## Source Observation Batch 09

`SOURCE-OBSERVATION-BATCH-09` is the gate-closing source observation batch. It
continues to treat all eighteen previously counted identities as duplicates and
selects only new concrete curated artifacts when the local manual gate is already
at `18/25`.

The Batch 09 curated targets are:

```text
qBittorrent 4.6.4 for Windows
FileZilla Pro 3.67.0 for Windows
OBS Studio 30.1 for Windows
HandBrake 1.7.3 for Windows
WinMerge 2.16.40 for Windows
calibre 7.8.0 for Windows
Python 3.12.3 for Windows
```

Prerequisite status checks:

```powershell
python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-01

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-02

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-03

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-04

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-05

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-06

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-07

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-08

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01
```

Create the batch scaffold:

```powershell
python scripts/eureka_artifact_gate.py source-plan --gate .eureka/artifact-gate/public-alpha-seed --manual-batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/source-observation-batch-09 --target-records 7

python scripts/eureka_artifact_gate.py source-template --collection .eureka/artifact-gate/source-observation-batch-09 --out .eureka/artifact-gate/source-observation-batch-09/source_observation_template.jsonl
```

Fill:

```text
.eureka/artifact-gate/source-observation-batch-09/source_url_list.jsonl
.eureka/artifact-gate/source-observation-batch-09/source_observations.jsonl
```

Useful bounded page observations for this batch include official release notes,
release tags, product pages, and project file-list pages for the seven targets
above. Treat official pages as identity metadata evidence when they identify the
product, version, release date, and platform/context. Treat archive-style file
list pages as corroboration unless paired with approved primary evidence.

Run the source batch:

```powershell
python scripts/eureka_artifact_gate.py source-ingest --collection .eureka/artifact-gate/source-observation-batch-09 --observations .eureka/artifact-gate/source-observation-batch-09/source_observations.jsonl

python scripts/eureka_artifact_gate.py source-validate --collection .eureka/artifact-gate/source-observation-batch-09

python scripts/eureka_artifact_gate.py source-to-evidence --collection .eureka/artifact-gate/source-observation-batch-09 --out .eureka/artifact-gate/source-observation-batch-09/manual_evidence_packets.jsonl

python scripts/eureka_artifact_gate.py source-report --collection .eureka/artifact-gate/source-observation-batch-09 --out .eureka/artifact-gate/source-observation-batch-09/source_collection_report.json

python scripts/eureka_artifact_gate.py source-status --collection .eureka/artifact-gate/source-observation-batch-09
```

Preserve prior batches with a cumulative generated handoff:

```powershell
Get-Content .eureka\artifact-gate\source-observation-batch-01\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-02\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-03\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-04\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-05\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-06\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-07\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-08\manual_evidence_packets.jsonl, .eureka\artifact-gate\source-observation-batch-09\manual_evidence_packets.jsonl | Set-Content -Encoding UTF8 .eureka\artifact-gate\source-observation-batch-09\manual_evidence_packets.cumulative.jsonl
```

Then refresh the manual and launch gates:

```powershell
python scripts/eureka_artifact_gate.py manual-ingest --batch .eureka/artifact-gate/manual-batch-01 --evidence .eureka/artifact-gate/source-observation-batch-09/manual_evidence_packets.cumulative.jsonl

python scripts/eureka_artifact_gate.py manual-validate --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_artifact_gate.py manual-review --batch .eureka/artifact-gate/manual-batch-01 --reviewer source_observation_batch_09 --out .eureka/artifact-gate/manual-batch-01/reviewed_artifact_records.jsonl

python scripts/eureka_artifact_gate.py manual-report --batch .eureka/artifact-gate/manual-batch-01 --out .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json

python scripts/eureka_artifact_gate.py manual-status --batch .eureka/artifact-gate/manual-batch-01

python scripts/eureka_public_alpha_launch_gate.py audit --bundle .eureka/staging/public-alpha --rehearsal-report .eureka/rehearsals/public-alpha/latest/rehearsal_report.json --artifact-gate-report .eureka/artifact-gate/manual-batch-01/artifact_gate_report.json --out .eureka/launch/public-alpha/latest
```

Expected Batch 09 result when all seven observations validate:

```text
source observations: 12 valid / 0 invalid
source evidence packets: 7
artifact verified packets: 7
cumulative manual evidence packets: 26
reviewed artifact gate count: 25/25
manual gate status: PASS
launch status: BLOCKED
```

Even at `25/25`, public launch is still blocked until non-corpus gates are
closed. The launch gate should consume the updated manual report and resolve the
official reviewed-artifact count blocker, while preserving deployment, release,
approval, verified-evidence-promotion, and unknown-authority blockers as
appropriate.

## Troubleshooting

- No eligible targets: inspect `source_candidate_plan.jsonl`; broad or
  under-specified records may need narrower artifact identity.
- Missing source identifier: fill `source_url` or `source_identifier`.
- `downloaded_file=true`: reject the observation; this workflow is metadata
  and page-observation only.
- Broad query: split it into concrete artifact identities before source work.
- Win98 driver missing hardware: add vendor, model, chipset, or device identity
  before artifact-gate work.
- Invalid observations: rerun `source-validate` and fix observer, source
  authority, observed fields, or unsafe flags.
- No evidence packets: supply valid observations or treat the collection as a
  source-observation handoff.
- Launch gate still blocked: expected until artifact evidence, deployment,
  release, and approval blockers clear.
- Duplicate identity: Firefox ESR 52.9.0, Sound Blaster 16 manual/User's
  Guide, `Mike Miller's Many Hats`, `7-Zip 19.00 for Windows`, `WinSCP 5.21.8`,
  `PuTTY 0.78 for Windows`, `Audacity 3.2.5 for Windows`, `VLC 3.0.20
  Vetinari`, `GIMP 2.10.38 for Windows`, `Notepad++ v8.6 for Windows`,
  `Inkscape 1.3.2 for Windows`, `LibreOffice 7.6.7 Community for Windows`, and
  `Apache OpenOffice 4.1.15 for Windows`, `Wireshark 4.2.3 for Windows`,
  `SumatraPDF 3.5.2 for Windows`, `Thunderbird 115.10.1 for Windows`,
  `IrfanView 4.67 for Windows`, and `Paint.NET 5.0.13 for Windows` must not be
  counted again after their respective batches. After Batch 09, `qBittorrent
  4.6.4 for Windows`, `FileZilla Pro 3.67.0 for Windows`, `OBS Studio 30.1 for
  Windows`, `HandBrake 1.7.3 for Windows`, `WinMerge 2.16.40 for Windows`,
  `calibre 7.8.0 for Windows`, and `Python 3.12.3 for Windows` are also
  duplicate identities. Treat new pages for counted identities as corroboration
  only.

## Deferred

Official artifact gate promotion beyond the local generated manual report,
verified artifact evidence promotion beyond genuinely supported packets,
broad/live evidence harvesting as default behavior, downloads, file fetching,
Wayback replay, extraction, install/emulation behavior, marketplace behavior,
external staging host provisioning, production hosting, TLS/domain setup,
production auth, public Workbench, public mutation, public contribution intake,
production review store, production index service, live IA indexing, public live
source fanout, release promotion, full discovery execution, and public launch
are deferred.
