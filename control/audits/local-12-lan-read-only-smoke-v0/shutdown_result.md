# Shutdown Result

The smoke script terminates the server process, verifies the port is no longer
serving Eureka, validates the explicit instance, and checks no local instance
state is committed.

Logs may exist only under the explicit instance root. `eureka-instance/**` must
remain ignored and uncommitted.
