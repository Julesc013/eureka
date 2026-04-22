"""GitHub Releases connector for the first recorded real-source Eureka slice."""

from runtime.connectors.github_releases.connector import GitHubReleasesConnector
from runtime.connectors.github_releases.source import (
    DEFAULT_GITHUB_RELEASES_FIXTURE_PATH,
    github_release_target_ref,
    load_github_release_source_records,
)

__all__ = [
    "DEFAULT_GITHUB_RELEASES_FIXTURE_PATH",
    "GitHubReleasesConnector",
    "github_release_target_ref",
    "load_github_release_source_records",
]
