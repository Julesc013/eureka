# Extension And Plugin Boundaries Spec

Plugins are future-gated. They should not be required for public alpha.

## Future Plugin Types

- source_connector
- renderer
- skin
- policy_pack
- pack_validator
- ranking_feature
- extractor
- action_backend
- native_bridge
- agent_provider
- compatibility_provider

## Required Manifest Fields

- plugin_id
- kind
- version
- input_contracts
- output_contracts
- permissions
- side_effects
- determinism
- network_access
- secrets_required
- max_runtime
- max_output_size
- test_fixtures
- policy_gates

No plugin enters the system without contract declaration, permission
declaration, test fixtures, policy gates, sandbox posture, and failure mode.

