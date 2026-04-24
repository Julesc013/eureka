# Identifier Policy

Eureka should prefer deterministic identifiers over fuzzy inference wherever the
domain permits.

## Identity Priority

The default order should be:

1. content hashes and other intrinsic identity
2. durable package-native or source-native identifiers
3. governed cross-source identity claims with evidence
4. fuzzy or heuristic similarity only when stronger identity is unavailable

## Important Identifier Families

Important identifier families include:

- content hashes
- source-native identifiers
- package-native identifiers
- SWHID later
- purl later
- DOI, ISBN, and similar identifiers later where the domain needs them

## Claim-Based Identity

Identity should be expressed through claims and evidence rather than premature
destructive merges.

Examples of future claim kinds include:

- same hash as
- same release as
- variant of
- successor of
- contains
- extracted from
- compatible with

## Bootstrap Note

`resolved_resource_id` remains a useful bootstrap seam. It is not yet the final
global identity system for Eureka.
