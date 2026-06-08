# Drift Root Cause Analysis

## Root Cause

The source-observation seam validator is intentionally strict: the R0 seam is
expected to remain free of task/control vocabulary and banned execution/import
patterns.

`runtime/source/observation/internet_archive_live_transport.py` retained a
Windows shell fallback for TLS verification failures. That fallback:

- imported `subprocess`
- carried reserved vocabulary in shell header names
- created an alternate execution path inside the source-observation package

That made the current source-observation baseline fail, even though the IA
specific live metadata validator still recognized the bounded urllib transport.

## Why This Was Not Fixed In The Validator

The validator was not stale for this specific finding. The shell fallback was no
longer the preferred TLS posture because the repo already records a verified
Python TLS trust repair. Removing the fallback is the safer alignment.

## Secondary Cause

The LOCAL-09 label in the same external family was stale relative to later queue
and handoff repair. Current focused validation passes that label without further
runtime changes.

