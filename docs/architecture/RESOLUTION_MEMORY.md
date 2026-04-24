# Resolution Memory

Resolution memory is not just search history. It is the durable record of what
worked, what failed, what sources helped, and what should be invalidated later.

## Memory Kinds

Eureka should keep distinct memory families rather than one opaque "global
memory":

- query memory
- evidence memory
- identity memory
- resolution memory
- absence memory
- source-health memory
- compatibility memory
- safety memory
- user strategy memory

## Resolution Memory Purpose

Resolution memory should capture reusable task patterns such as:

- interpreted intent
- useful sources
- bad interpretations
- successful result clusters
- invalidation rules

This is one of Eureka's key future differentiators because it turns successful
investigations into reusable resolver knowledge rather than forcing repeated
manual work.

## Privacy Boundary

Resolution memory is not automatically shareable.

The safe default is:

- public source evidence may become shareable
- extraction outputs may become shareable when rights allow
- user behavior and local context remain private by default

## Near-Term Direction

The first practical implementation should be a private local memory seam rather
than a shared multi-user service.
