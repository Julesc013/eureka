# External Full Discovery Rerun 05

Task: `EXTERNAL-FULL-DISCOVERY-RERUN-05`

Status: `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`

This handoff exists because docs/control commits were made after the latest
green full-discovery ingest. The prior green run remains useful historical
evidence, but it is stale for the current `dev` HEAD.

## Handoff Base Head

```text
branch: dev
handoff_base_head: 4f2b18863d7b5df2bf2f0b242f6aafa06933ae98
```

The external summary must match the operator's current checked-out `dev` HEAD
at run time. This handoff commit and any later explicit continuation commits
will naturally advance `HEAD`.

## Prior Green Evidence

`SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-04` records
`source_snapshot_full_discovery_rerun_04` as green for:

```text
c7ae8623a21d44e4bcb20d48e1565505adc6fb50
```

That evidence is not current to this handoff HEAD.

## Operator Action

Run the full discovery harness outside the AI session:

```powershell
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/source_snapshot_full_discovery_rerun_05
```

Do not paste raw stdout or stderr into chat. Return compact artifacts only.

## Resume Rule

After the external run completes, resume with:

```text
SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-05
```

If the compact summary is red, choose the narrowest failure-family repair task
instead of public-alpha readiness or `dev -> main` promotion.

## Boundary

This handoff does not run full discovery inside the AI session, launch public
alpha, promote `dev -> main`, create reviewed artifact records, create verified
artifacts, or mutate product runtime behavior.
