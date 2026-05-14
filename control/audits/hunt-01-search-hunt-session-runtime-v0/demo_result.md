# Demo Result

`scripts/demo_search_hunt_session.py` creates or reuses a session for `sampleproject`, attaches local summaries, runs `created -> running -> paused -> running -> complete`, proves invalid transition rejection, and emits transition history.

The demo records no WorkUnits and performs no source probes or model/provider calls.
