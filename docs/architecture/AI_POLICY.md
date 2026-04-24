# AI Policy

Eureka should be AI-capable, not AI-dependent.

## Truth Hierarchy

The default hierarchy is:

```text
deterministic evidence
> structured metadata
> graph rules
> lexical search
> embeddings and rerankers
> LLM inference
```

The model is never the source of truth.

## Acceptable AI Roles

Optional AI may later help with:

- vague intent parsing
- query rewriting
- difficult extraction from messy text
- grounded explanation drafting
- limited reranking support

## Forbidden Uses

AI must not become:

- canonical fact source
- identity authority
- trust authority
- hidden merge engine

## Capability Levels

Reasonable capability levels are:

1. no AI
2. classical normalization and rules
3. embeddings or rerankers
4. small local model helpers
5. larger local or remote fallback helpers

Every higher level should remain optional and replaceable by deterministic logic
when feasible.
