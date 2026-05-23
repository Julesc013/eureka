# WorkUnit Queue Summary

LOCAL-07 adds `runtime/worker/workunit_queue` and the manifest-defined `workunit_queue` SQLite store at `db/workunit_queue.sqlite`.

The queue supports creating, listing, inspecting, pausing, resuming, cancelling, blocking, completing, and failing local WorkUnit records. It records transition history and rejects invalid transitions.

The queue does not execute any underlying work.
