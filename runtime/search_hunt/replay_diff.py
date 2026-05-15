"""Expected-versus-actual replay diff helpers."""

from typing import Any, Mapping

from .replay_records import HuntReplayDiff


def diff_replay_outputs(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> HuntReplayDiff:
    expected_summary = dict(expected)
    actual_summary = {key: actual.get(key) for key in expected_summary}
    differences = []
    for key, expected_value in expected_summary.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            differences.append({"field": key, "expected": expected_value, "actual": actual_value})
    matched = not differences
    return HuntReplayDiff(
        status="matched" if matched else "diff",
        matched=matched,
        differences=tuple(differences),
        expected_summary=expected_summary,
        actual_summary=actual_summary,
        warnings=(),
    )
