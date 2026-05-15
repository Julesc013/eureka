# Secret Scan Summary

- broad: matches=3561, exit=0
- long_openai_key: matches=1, exit=0
- anthropic_key: matches=0, exit=1
- private_key: matches=3, exit=0
- env_secret_assignment: matches=0, exit=1

Inspection result: broad matches are policy/example/test text. High-confidence assignment scan found no committed live provider secret in Q57 artifacts.
