"""Small robots.txt policy evaluator for safe web fetching."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable
from urllib.parse import urlparse


RobotsFetcher = Callable[[str], tuple[int, str]]


@dataclass(frozen=True)
class RobotsDecision:
    allowed: bool
    status: str
    robots_url: str
    matched_rule: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "status": self.status,
            "robots_url": self.robots_url,
            "matched_rule": self.matched_rule,
            "error": self.error,
        }


class AllowAllRobotsClient:
    def can_fetch(self, url: str, user_agent: str) -> RobotsDecision:
        return RobotsDecision(True, "allowed_by_test_client", robots_url=_robots_url(url))


class RobotsTxtClient:
    def __init__(self, fetcher: RobotsFetcher, *, fail_closed: bool = True) -> None:
        self._fetcher = fetcher
        self._fail_closed = fail_closed
        self._cache: dict[str, tuple[int, str]] = {}

    def can_fetch(self, url: str, user_agent: str) -> RobotsDecision:
        robots_url = _robots_url(url)
        if not robots_url:
            return RobotsDecision(False, "blocked", robots_url="", error="invalid_robots_url")
        try:
            status, body = self._cache.get(robots_url) or self._fetcher(robots_url)
            self._cache[robots_url] = (int(status), str(body or ""))
        except Exception as exc:
            return RobotsDecision(not self._fail_closed, "robots_unreachable", robots_url, error=str(exc))
        if status >= 500:
            return RobotsDecision(not self._fail_closed, "robots_unavailable", robots_url, error=f"http_{status}")
        if status >= 400:
            return RobotsDecision(True, "robots_missing", robots_url)
        allowed, rule = _evaluate_robots(str(body or ""), url, user_agent)
        return RobotsDecision(allowed, "allowed" if allowed else "blocked_by_robots", robots_url, matched_rule=rule)


def _robots_url(url: str) -> str:
    parsed = urlparse(str(url or ""))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def _evaluate_robots(body: str, url: str, user_agent: str) -> tuple[bool, str]:
    parsed = urlparse(str(url or ""))
    target = parsed.path or "/"
    if parsed.query:
        target = f"{target}?{parsed.query}"
    agent_token = _agent_token(user_agent)
    groups = _parse_groups(body)
    applicable = [rules for agents, rules in groups if agent_token in agents]
    if not applicable:
        applicable = [rules for agents, rules in groups if "*" in agents]
    if not applicable:
        return True, ""
    rules = [rule for group in applicable for rule in group]
    best: tuple[int, str, bool] | None = None
    for directive, pattern in rules:
        if pattern == "":
            continue
        if _rule_matches(pattern, target):
            current = (len(pattern), f"{directive}:{pattern}", directive == "allow")
            if best is None or current[0] > best[0] or (current[0] == best[0] and current[2] and not best[2]):
                best = current
    if best is None:
        return True, ""
    return best[2], best[1]


def _parse_groups(body: str) -> list[tuple[set[str], list[tuple[str, str]]]]:
    groups: list[tuple[set[str], list[tuple[str, str]]]] = []
    agents: set[str] = set()
    rules: list[tuple[str, str]] = []
    for raw_line in str(body or "").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().casefold()
        value = value.strip()
        if key == "user-agent":
            if agents and rules:
                groups.append((agents, rules))
                agents, rules = set(), []
            agents.add(value.casefold())
        elif key in {"allow", "disallow"} and agents:
            rules.append((key, value))
    if agents:
        groups.append((agents, rules))
    return groups


def _rule_matches(pattern: str, path: str) -> bool:
    escaped = re.escape(pattern).replace(r"\*", ".*")
    if escaped.endswith(r"\$"):
        escaped = escaped[:-2] + "$"
    else:
        escaped += ".*"
    return re.match("^" + escaped, path) is not None


def _agent_token(user_agent: str) -> str:
    value = str(user_agent or "").casefold()
    match = re.search(r"[a-z][a-z_-]+", value)
    return match.group(0) if match else "*"
