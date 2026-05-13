# Migration Guard Result

LOCAL-02 adds check-only migration guard behavior:

- store manifest written by init
- migration state written by init
- schema version written by init
- unsupported versions fail closed
- migration status command is read-only
- destructive migrations remain forbidden
