# Resolution Memory

Resolution memory is not just search history. It is the durable record of what
worked, what failed, what sources helped, and what should be reconsidered
later.

## Current Status

Resolution Memory v0 is now implemented as an explicit local seam under
`runtime/engine/memory/`.

Current v0 behavior is intentionally narrow:

- memory is created manually and explicitly from an existing persisted
  completed resolution run
- memory is stored as local JSON under a caller-provided bootstrap
  `memory_store_root`
- memory is exposed through gateway public boundaries reused by current web,
  CLI, and local HTTP API surfaces
- memory is not cloud/shared memory, not personalization, and not private
  user-history tracking
- invalidation exists only as compact `invalidation_hints` placeholders; no
  invalidation engine is implemented yet

## Implemented Memory Kinds

Runtime-created Resolution Memory v0 records currently support:

- `successful_resolution`
- `successful_search`
- `absence_finding`

The broader `source_usefulness` family is still a governed future shape rather
than a runtime-populated v0 record kind.

## Resolution Memory Purpose

Resolution Memory v0 captures compact reusable fields such as:

- source run id
- raw query or requested value when present
- `resolution_task` summary when the source run carries one
- checked source ids and source families
- compact result summaries or one absence report
- useful source ids derived honestly from the run
- compact evidence summaries
- bootstrap invalidation hints

This is one of Eureka's key future differentiators because it turns successful
investigations into reusable resolver knowledge rather than forcing repeated
manual work.

## Privacy Boundary

Resolution Memory v0 is local by default.

The safe default is:

- public source evidence may later become shareable
- extraction outputs may later become shareable when rights allow
- personal user behavior, private local paths, and host-specific local context
  stay private by default

## Still Deferred

Resolution Memory v0 does not yet implement:

- automatic memory creation
- invalidation logic
- planner reuse driven directly by memory
- ranking or recommendation changes from memory
- shared or cloud memory
- user personalization or private-history profiling
