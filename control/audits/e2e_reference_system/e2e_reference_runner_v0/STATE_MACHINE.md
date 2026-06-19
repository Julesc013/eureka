# State Machine

Supported states:

- created
- planned
- running
- paused
- completed
- failed
- cancelled
- policy_blocked

Forbidden:

- resume a non-paused run;
- pause a terminal run;
- cancel a terminal run;
- execute provider code from replay;
- enter live-shadow without separate provider approval;
- create reviewed truth from runner state.
