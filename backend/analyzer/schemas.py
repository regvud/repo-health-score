from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class RepoRawData:
    repo_data: dict[str, Any]
    commit_activity: list[dict[str, Any]] | None
    closed_issues: list[dict[str, Any]]
    releases: list[dict[str, Any]]
    cached: bool


@dataclass
class SignalResult:
    score: int | None
    value: str
    status: Literal["good", "warning", "bad", "neutral"]


@dataclass
class SignalSchema:
    name: str
    label: str
    weight: int
    score: int | None
    value: str
    status: Literal["good", "warning", "bad", "neutral"]


@dataclass
class RepoMetaSchema:
    stars: int | None
    forks: int | None
    open_issues: int | None
    description: str | None
    cached: bool


@dataclass
class HealthReportSchema:
    repo: str
    score: int
    signals: list[SignalSchema]
    meta: RepoMetaSchema
