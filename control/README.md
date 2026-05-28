# Control

`control/` holds governance assets that manage Eureka rather than implementing
runtime behavior.

Current contents include:

- `audits/`: audit packs, review evidence, and generated samples
- `inventory/`: structured matrices, status files, and command/test registries
- `policies/`: repo and product-boundary policies
- `backlog/`: governed future-work triage
- `research/`: bounded research notes kept separate from product truth

`control/` may record whether a capability is planned, blocked, validated, or
approved. It must not secretly define runtime behavior or accepted product truth
without the matching contracts/runtime evidence.

For current status, start with [../README.md](../README.md) and
[../docs/BOOTSTRAP_STATUS.md](../docs/BOOTSTRAP_STATUS.md).
