# Pack Lifecycle

Pack Lifecycle v0 is shared guidance for future source, evidence, index, and
contribution pack contracts. It is not runtime behavior and does not create a
hosted submission queue.

## Statuses

`draft`

The pack is being authored. It may be incomplete.

`local_private`

The pack is local-only and must not be shared without review. This is the safe
default for newly created packs.

`validated_local`

Generic status for a pack that passed local validation. Source Pack Contract v0
keeps this as lifecycle guidance; Evidence Pack Contract v0 includes it in the
manifest enum for claim/observation bundles that have passed local validation
but are not yet intended as shareable candidates.

`shareable_candidate`

The pack is intended to be public-safe after validation. It is still not
canonical, not indexed, not uploaded, and not master-index accepted.

`submitted`

Future status for a pack submitted to a review workflow. P34 does not implement
submission.

`quarantined`

Future review status for a pack isolated because of privacy, rights, safety, or
quality concerns.

`review_required`

Future review status for packs needing human or governed review before any
public use.

`accepted_public`

Future status for a reviewed pack accepted into a public-safe catalog or master
index. P34 does not create an acceptance path.

`rejected`

The pack failed review or validation and must not be accepted.

`superseded`

The pack has been replaced by a newer pack.

## Boundary

A lifecycle status is not executable authority. It does not grant network
access, local filesystem access, import rights, upload rights, plugin
execution, artifact distribution rights, malware safety, rights clearance, or
production support.
