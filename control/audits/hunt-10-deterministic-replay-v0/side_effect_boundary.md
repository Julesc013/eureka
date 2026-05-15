# Side-Effect Boundary

Allowed side effects are local replay records, local temporary workflow records in the explicit instance, and safe deterministic worker state transitions. Replay does not run source probes, extraction, AI/model providers, browser research, artifact acquisition, artifact launch, source sync, deployment, site output writes, or master-index mutation.
