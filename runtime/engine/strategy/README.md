## Bounded Strategy Profiles

This package defines the first bounded user-strategy / intent-profile seam for
Eureka.

It is intentionally small:

- a fixed set of bootstrap strategy profiles
- compact descriptive emphasis hints
- no persistence
- no personalization
- no ranking
- no trust or policy scoring

The current profiles are:

- `inspect`
- `preserve`
- `acquire`
- `compare`

These profiles do not change underlying resolution truth, evidence, or
representation data. They only provide bounded recommendation emphasis that can
shape later action routing.
