"""Report builders for local evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any, Mapping

from .latency import summarize_latency


@dataclass(frozen=True)
class LocalEvalReport:
    base_url: str
    suite_results: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "fixed local query suite only",
        "local reviewed index only",
        "latency values are smoke estimates",
    )

    def to_dict(self) -> dict[str, Any]:
        case_results = [case for suite in self.suite_results for case in suite.get("cases", [])]
        failed = [case for case in case_results if not case.get("passed")]
        warnings = list(self.warnings)
        for suite in self.suite_results:
            warnings.extend(str(item) for item in suite.get("warnings", []))
        return {
            "schema_version": "local_eval_report.v0",
            "status": "pass" if not failed else "fail",
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "base_url": self.base_url,
            "suite_count": len(self.suite_results),
            "case_count": len(case_results),
            "passed_case_count": len(case_results) - len(failed),
            "failed_case_count": len(failed),
            "suite_results": [dict(item) for item in self.suite_results],
            "latency": summarize_latency(case_results),
            "external_network_used": False,
            "source_probe_executed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "download_install_execute_performed": False,
            "site_dist_mutated": False,
            "master_index_mutated": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
            "warnings": warnings,
            "limitations": list(self.limitations),
        }


def build_json_report(base_url: str, suite_results: list[Mapping[str, Any]]) -> dict[str, Any]:
    return LocalEvalReport(base_url=base_url, suite_results=tuple(suite_results)).to_dict()


def build_markdown_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "# Local Eval Summary",
        "",
        f"- status: {report.get('status')}",
        f"- base_url: {report.get('base_url')}",
        f"- suites: {report.get('suite_count')}",
        f"- cases: {report.get('passed_case_count')}/{report.get('case_count')} passed",
        f"- external_network_used: {str(report.get('external_network_used')).lower()}",
        f"- source_probe_executed: {str(report.get('source_probe_executed')).lower()}",
        f"- lan_enabled: {str(report.get('lan_enabled')).lower()}",
        "",
        "## Suites",
    ]
    for suite in report.get("suite_results", []):
        lines.append(f"- {suite.get('suite')}: {suite.get('status')} ({suite.get('passed_case_count')}/{suite.get('case_count')} passed)")
    latency = report.get("latency", {})
    lines.extend(
        [
            "",
            "## Latency",
            f"- max_elapsed_ms: {latency.get('max_elapsed_ms', 0)}",
            f"- average_elapsed_ms: {latency.get('average_elapsed_ms', 0)}",
            "",
            "## Limitations",
        ]
    )
    for item in report.get("limitations", []):
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def dumps_report(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
