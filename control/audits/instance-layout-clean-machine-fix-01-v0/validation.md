# Validation

The clean-machine path now passes through:

- shared path resolver policy validation
- LOCAL-13 clean-machine bootstrap validator
- the two previously failing clean-machine unit tests

The repair did not move or delete operator instance state and did not run source probes, extraction, model/provider calls, or deployment.
