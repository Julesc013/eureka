# Eureka Local Acceptance Runbook

This session evaluates Eureka as a local product. Automated checks have prepared the instance, but only operator feedback can produce an acceptance verdict.

## Start

From the repo root, run:

```powershell
python scripts/eureka.py `
  --instance ../instances/eureka-e2e-acceptance-v0 `
  serve `
  --mode exploration `
  --host 127.0.0.1 `
  --port 8765
```

Open:

```text
http://127.0.0.1:8765/explore
```

The service is intended to bind only to loopback. Do not expose it with a tunnel or proxy.

## Evaluate

1. First impression
   - Without reading architecture docs, what do you think Eureka does?
   - What is the first action you expect to take?
   - Is Search versus Hunt understandable?
   - Is local/private posture obvious?

2. Search and result lanes
   - Search for:
     - `old blue FTP client for XP`
     - `manual for Sound Blaster CT1740`
     - `latest Firefox before XP support ended`
     - `article about ray tracing in a 1994 magazine`
     - one unfamiliar query of your choice
   - For each query, check whether status, authority, uncertainty, why matched, and next steps are understandable.
   - Confirm no result implies reviewed truth unless it is actually reviewed.

3. Hunt lifecycle
   - Start one synthetic Hunt.
   - Inspect planned work.
   - Advance one step.
   - Pause and resume.
   - Run to completion if practical.
   - Confirm disabled controls and provider/network posture are clear.

4. Events and provenance
   - Inspect events, source/evidence references, warnings, and limitations.
   - Note whether IDs, paths, or implementation details overwhelm the product experience.

5. Replay and compare
   - Replay the completed run.
   - Create or inspect a second synthetic run.
   - Compare added, removed, unchanged, status, work, and boundary differences.

6. Degraded states
   - Inspect at least a no-result query, unavailable live-shadow posture, synthetic-excluded posture, invalid run ID, and cancelled/incomplete run if practical.
   - Confirm failures are honest, recoverable, and do not show stack traces or private secrets.

7. Terminology
   - Rate whether these terms should stay visible, be renamed, be explained, or move to advanced detail:
     - Search
     - Hunt
     - ResolutionRun
     - WorkUnit
     - Preview result
     - Candidate
     - Near miss
     - Need
     - Absence
     - Status
     - Authority
     - Reviewed
     - Synthetic

8. Optional frozen-candidate calibration
   - If read-only IA candidate material is visible, inspect up to three items for evidence clarity only.
   - Do not record review decisions, promote candidates, or create reviewed records.

## Finish

Complete `OPERATOR_FEEDBACK_FORM.md` and return it verbatim. The system must not infer your verdict.
