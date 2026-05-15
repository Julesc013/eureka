# Remaining Risks

- The surface packets are fixture-only and local-only; they are not production live-source support.
- The reviewed index candidate remains evidence-local/transient. Q61 should harden reviewed-index persistence and reload behavior.
- Existing AIDE eval failures remain outside the Q60 slice. The repeated Q60 verification also timed out on `eval run` after 10 minutes, so the latest available 127 pass / 9 fail report was used as the recorded AIDE eval evidence.
- The local branch is both ahead and behind origin/dev; integration must wait until the other machine pauses and the operator confirms it is safe.
- Q60 was not committed in isolation because its product/test paths remain untracked together with prior Q58/Q59 slice paths; staging them now would collapse multiple phases into one commit.
