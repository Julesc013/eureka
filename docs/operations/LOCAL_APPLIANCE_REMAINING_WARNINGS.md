# Local Appliance Remaining Warnings

LOCAL-14 disposes one known warning: the pre-existing runtime leakage gate
findings.

The count is unchanged across LOCAL baselines, so LOCAL did not increase
leakage. The warning does not block HUNT/SYN/F0 planning, but it does block
automatic main promotion. `LOCAL-LEAKAGE-01` remains the child task for
reconciling the leakage gate before promotion.

Full unittest discovery may still fail with historical discovery-lane output.
That failure is recorded as a warning and must not be normalized into a clean
pass.
