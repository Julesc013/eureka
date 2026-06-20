# Fault Model

The resilience suite includes deterministic offline fault fixtures:

- provider outage posture;
- rate-limit retry posture;
- malformed input rejection;
- corrupt bundle rejection;
- worker restart through replay;
- partial recovery;
- event replay hash-chain validation;
- synthetic rollback through the synthetic truth path.

No case calls a live provider.
