# Search Hunt Workflow Runbook

Initialize a local instance, set an operator token, run the workflow smoke, then start the local server and run workbench/API smokes.

The workflow may create local Hunt, SearchNeed, WorkUnit, command, steering, exhaustion, and safe worker result records. It must not execute policy-blocked future work.
