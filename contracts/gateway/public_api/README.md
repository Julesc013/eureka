# Gateway Public API

This directory contains draft public API contracts for the normal online path used by Eureka surfaces.

Web should use these contracts rather than engine internals. Native should also prefer this boundary except where an explicit future offline mode says otherwise.

Internal broker, relay, worker, scheduler, and auth protocols remain out of scope here. They are runtime concerns, not public API promises.
