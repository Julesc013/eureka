# E2E Hunt Exploration UI Runbook

The Explore workspace is available from the local appliance service at:

```text
/explore
```

It is a private local operator surface for Preview Index search, synthetic Hunt creation, durable run inspection, replay, and run comparison.

## Build And Inspect

```text
GET /explore?q=WinFTP%20XP%20client
GET /api/v1/explore?q=WinFTP%20XP%20client
```

The page shows Preview Index lanes, status and authority labels, why records matched, why they ranked, missing information, permitted actions, unavailable actions, and boundary flags.

If the Preview Index is missing, the workspace degrades to an empty preview panel and reports the missing index. It does not create records.

## Start Synthetic Hunt

```text
POST /explore/run/start
POST /api/v1/explore/run/start
```

Required form fields:

```text
operator_token=<configured local token>
q=<query>
```

The route runs the shared E2E Reference Runner in synthetic mode and writes a durable generated bundle under:

```text
.eureka/e2e-reference/runs/<run-id>/
```

## Inspect Runs

```text
GET /explore/runs
GET /explore/run/<run-id>
GET /api/v1/explore/runs
GET /api/v1/explore/run/<run-id>
```

Run listing and detail routes read durable bundles. They do not depend on process-local cache.

## Replay And Compare

```text
POST /explore/run/<run-id>/replay
GET /explore/compare?left=<run-id>&right=<run-id>
```

Replay validates a bundle and writes only a generated replay report in the run bundle. Compare is read-only.

## Controls

Synthetic runs currently complete synchronously. Pause, resume, cancel, and step controls are rendered disabled for terminal runs and return a blocked response if submitted.

## Safety Invariants

- Loopback-only operator workspace.
- POST routes require an operator token.
- GET routes do not mutate state.
- No live providers or network calls.
- No downloads or file payload fetches.
- No review decisions.
- No reviewed records.
- No reviewed/master or public-index mutation.
- No public exposure.
- License posture remains restricted source-available.
