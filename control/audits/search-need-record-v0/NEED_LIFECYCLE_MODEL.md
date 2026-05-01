# Need Lifecycle Model

Lifecycle status values include draft/example states, unresolved, local private,
public aggregate candidate, rejected by privacy filter, and future merge,
supersede, or resolve states.

P62 does not implement lifecycle storage or status transitions. The lifecycle
schema keeps runtime store, probe creation, candidate creation, and master-index
mutation flags false.
