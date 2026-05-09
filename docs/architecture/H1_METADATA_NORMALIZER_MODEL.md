# H1 Metadata Normalizer Model

The H1 normalizer model is source-specific at the edge and shared in the middle. Seven thin modules call `normalizer_common.normalize_h1_fixture`, which enforces no-live boundaries, candidate-only mappings, and shared output semantics.

The model prepares H1-BUNDLE-03 by proving fixture parsing and replay shape before any future approved live-probe envelope.
