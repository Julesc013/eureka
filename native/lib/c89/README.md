# C89 Contract Library

The C89 library is a small bounded helper layer for native clients that need to
recognize snapshot, relay, and action manifest contract tokens. It is not a full
JSON parser and does not perform file I/O, network access, downloads, installs,
execution, or platform GUI work.

All functions return explicit status codes and use caller-provided buffers.
