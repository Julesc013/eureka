# Behavior Test Summary

Behavior tests cover:

- stable `SourceId` validation
- invalid source id rejection
- `SourceRecord` JSON round trip
- source policy blocked and allowed decisions
- metadata request serialization
- metadata response fingerprinting from explicit payload material
- normalization to `NormalizedObservation`
- evidence candidate creation without acceptance
- review item creation without a review decision
- demo execution without network use
- runtime package isolation from connector modules

The tests assert behavior rather than artifact existence alone.
