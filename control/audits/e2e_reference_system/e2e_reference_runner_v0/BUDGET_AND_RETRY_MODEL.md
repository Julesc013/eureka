# Budget And Retry Model

The runner supports:

- maximum WorkUnits;
- maximum attempts per WorkUnit;
- maximum event count;
- maximum elapsed seconds;
- maximum result records per WorkUnit;
- fail-fast or continue-with-partial-failure policy.

Budgets emit explicit events and do not imply source absence. Tests use a
deterministic clock and do not sleep.
