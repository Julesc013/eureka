# Runtime

`runtime/` holds product execution areas. Bootstrap separates engine, gateway, and connectors so their dependencies stay explicit before any real logic is added.

- `engine/`: core resolution, preservation, reconstruction, and snapshotting logic
- `gateway/`: public-facing runtime boundary, brokering, scheduling, and publishing
- `connectors/`: bounded acquisition adapters that feed governed engine interfaces

