# Snapshot Relay Runbook


This document describes the SNAPSHOT-RELAY-00 foundation. Snapshots are read-only data products built from reviewed local records or fixture-reviewed records. Relays are read-only projections over snapshots. They do not run live source actions, mutate stores, include private local state, include raw live responses, deploy a public service, or claim production/public launch readiness.

Core boundaries:
- reviewed records only
- source and evidence summaries, not raw evidence blobs
- integrity manifests use deterministic public hashes only
- private signing keys are forbidden
- capability profiles disable live source actions, review, mutation, downloads, and extraction
- public, native, lite, text, files, and API projections are read-only

Next task: PUBLIC-ALPHA-READONLY-00.
