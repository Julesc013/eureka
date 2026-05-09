# Connector Fixture Replay Contract

Fixture replay proves that a connector family can parse and normalize committed
fixtures without source access.

Allowed inputs are committed, synthetic, or public-safe fixtures. Forbidden
inputs include credentials, cookies, live-call evidence, downloaded binaries, and
private files. Replay output is a candidate-only envelope; it is not accepted
source truth or evidence.

Fixture replay must record:

- no network used
- no live source used
- no public/master index mutation
- no evidence, candidate, or public truth acceptance
