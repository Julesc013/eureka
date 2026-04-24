# Eureka Thesis

Eureka is not merely "archive search." It is a software-first temporal object
resolver that should help users find, verify, compare, explain, and act on
digital objects across current and archived ecosystems with minimal detective
work.

The product should accept vague human requests such as:

- `Windows 7 apps`
- `driver for Win98`
- `old blue FTP client for XP`
- `article about ray tracing in a 1994 magazine`
- `latest Firefox before XP support ended`
- `manual for Sound Blaster CT1740`

Those requests should not terminate in a shallow pile of outer containers,
collection pages, or misleading keyword matches. The resolver should aim for
the smallest useful actionable unit that can be explained honestly with bounded
evidence and clear uncertainty.

## Product Class

Eureka should evolve toward a:

- streaming resolver rather than a static search box
- provenance-aware evidence system rather than a hidden relevance engine
- decomposition-aware archive navigator rather than a container-only catalog
- compatibility-aware action router rather than a generic download list
- resumable investigation system rather than a one-shot request handler

## Current Status

This thesis is accepted product direction. It is not a claim that the current
repo already implements the full resolver.

Today the repo remains:

- bootstrap and pre-product
- Python stdlib in the executable lane
- bounded and deterministic
- honest about deferred semantics

The current implementation proves many domain seams and multiple surfaces, but
it does not yet provide durable investigation runs, shared evidence services,
production indexing, live source federation, or a production backend stack.
