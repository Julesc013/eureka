# Search Hunt Closeout

Run the closeout lane from a clean `dev` checkout after HUNT-11:

```text
python scripts/audit_search_hunt_closeout.py --json
python scripts/validate_search_hunt_closeout.py
python -m unittest tests.operations.test_search_hunt_closeout
```

The closeout reads repo-local inventories and audit reports only. It does not
open source probes, extraction, providers, browser automation, downloads, or
deployment.

Expected result after remediation is `pass`: HUNT is complete, no hard blockers
or remaining HUNT closeout warnings remain, SYN can start, F0 can resume, and
main promotion is separated into a review task.
