# Validation Matrix

The remediation validation matrix requires:

- all HUNT validators pass
- workflow smoke passes
- full unittest discovery passes
- generated artifact cleanliness passes after commit
- architecture boundaries pass
- runtime leakage gate has zero new HUNT violations

The detailed machine-readable matrix is in
`control/inventory/hunt_remediation_validation_matrix.json`.
