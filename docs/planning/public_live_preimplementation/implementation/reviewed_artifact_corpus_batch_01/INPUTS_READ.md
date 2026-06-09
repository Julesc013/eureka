# Inputs Read

Primary inputs:

```text
AGENTS.md
README.md
.aide/queue/index.yaml
.aide/context/latest-task-packet.md
docs/planning/public_live_preimplementation/implementation/manual_artifact_observation_batch_00/**
docs/planning/public_live_preimplementation/implementation/human_artifact_review_batch_00/**
evals/hard_queries/artifact_observations/batch_00/**
evals/hard_queries/artifact_reviews/batch_00/**
evals/hard_queries/reviewed_artifact_records/batch_00/**
evals/hard_queries/artifact_record_gate/gate_01/**
evals/hard_queries/reviewed_seed_corpus/**
tests/evals/**
tests/runtime/test_surface_*artifact*.py
```

Missing or substituted paths:

```text
evals/hard_queries/human_artifact_reviews/batch_00/ was not present.
Used evals/hard_queries/artifact_reviews/batch_00/ as the actual human artifact review output.

evals/hard_queries/reviewed_artifact_corpus/ was not present before this task.
Created evals/hard_queries/reviewed_artifact_corpus/batch_01/.
```

Current input head before this task's commit:

```text
b7253dc3964ef8ac7ef6235965bdd2728e7d6690
```

