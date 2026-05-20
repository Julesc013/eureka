# View Model And Packet Boundary

Runtime services produce packets and view models. Surfaces render packets. Surfaces do not own product truth. Contracts own packet schemas and projection contracts. Runtime owns implementation and local validation helpers, not contract authority. Examples are fixtures only.

The Workbench uses a richer projection of the same packets. Public, native, relay, and snapshot clients use restricted projections. Permission and visibility vary by projection profile; semantic truth does not fork by surface.

Reserved packet families: SearchPacket, SearchRequestPacket, CompiledQueryPacket, ResolutionRunPacket, ResultLanePacket, HuntStatePacket, WorkUnitPacket, SourceRecordPacket, SourceCacheRecordPacket, EvidencePacket, CandidatePacket, ReviewPacket, PromotionPreviewPacket, ReviewedRecordPacket, AbsencePacket, ActionPosturePacket, CoverageReportPacket, DiscoveryTrailPacket, SnapshotPacket, RelayPacket, and OpsStatusPacket.

SEARCH-INTERACTION-00 will define search request, compiled query, resolution run, controls, feedback, result lane, absence, coverage, and discovery trail contracts. WORKBENCH-FOUNDATION-00 only reserves locations and projection rules.
