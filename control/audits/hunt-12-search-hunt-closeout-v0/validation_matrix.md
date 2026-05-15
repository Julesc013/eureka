# Validation Matrix

The HUNT closeout validator runs or classifies all HUNT validators, the local
appliance closeout validator, generated-artifact cleanliness, architecture
boundaries, and focused HUNT-12 tests.

Known historical validator failures caused only by old queue-next assertions are
disposed as warnings. Focused HUNT-12 tests and scripts are expected to pass.
Full unittest discovery remains optional and broad; timeout in this environment
is disposed as a warning rather than a blocker.
