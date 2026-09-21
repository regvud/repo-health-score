import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from ..cache import get_cache, set_cache
from ..config import config
from ..exceptions import GitHubNotFoundError, GitHubRateLimitError
from ..regex import GITHUB_REPO_URL
from ..schemas import RepoRawData
from .consts import (
    BASE_HEADERS,
    GITHUB_API_BASE,
    ISSUES_PER_PAGE,
    LOOKBACK_DAYS,
    RELEASES_PER_PAGE,
    REQUEST_TIMEOUT,
    STATS_RETRY_DELAY,
)


def parse_github_url(url: str) -> tuple[str, str]:
    match = GITHUB_REPO_URL.match(url.strip().rstrip("/"))
    if not match:
        raise ValueError("Not a valid GitHub repository URL (expected https://github.com/owner/repo)")

    owner = match.group(1)
    repo = match.group(2)

    return owner, repo


async def process_http_request(client: httpx.AsyncClient, url: str, params: dict | None = None) -> Any:
    response = await client.get(url, params=params)

    if response.status_code == 404:
        raise GitHubNotFoundError()

    if response.status_code in (403, 429):
        remaining = response.headers.get("X-RateLimit-Remaining", "1")
        if remaining == "0":
            raise GitHubRateLimitError()

    # Stats endpoints return 202 while GitHub computes the data — retry once
    if response.status_code == 202:
        await asyncio.sleep(STATS_RETRY_DELAY)
        response = await client.get(url, params=params)
        if response.status_code == 202:
            return None

    response.raise_for_status()
    return response.json()


async def fetch_repo_data(owner: str, repo: str) -> RepoRawData:
    cache_key = f"{owner}/{repo}"
    cached = get_cache(cache_key)
    if cached is not None:
        return RepoRawData(**{**cached, "cached": True})

    headers = {**BASE_HEADERS}
    if config.github_token:
        headers["Authorization"] = f"Bearer {config.github_token}"

    cutoff = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    base = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    try:
        async with httpx.AsyncClient(headers=headers, timeout=REQUEST_TIMEOUT) as client:
            repo_data, commit_activity, closed_issues, releases = await asyncio.gather(
                process_http_request(client, base),
                process_http_request(client, f"{base}/stats/commit_activity"),
                process_http_request(client, f"{base}/issues",
                                     {"state": "closed", "sort": "updated", "direction": "desc",
                                      "per_page": str(ISSUES_PER_PAGE)}),
                process_http_request(client, f"{base}/releases", {"per_page": str(RELEASES_PER_PAGE)}),
            )
    except (GitHubNotFoundError, GitHubRateLimitError):
        raise
    except httpx.TimeoutException as exc:
        raise TimeoutError(f"GitHub API timed out for {owner}/{repo}") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"GitHub API returned {exc.response.status_code} for {owner}/{repo}") from exc

    if repo_data is None:
        raise GitHubNotFoundError()

    closed_in_90d = [
        issue for issue in (closed_issues or [])
        if "pull_request" not in issue and (issue.get("closed_at") or "") >= cutoff
    ]

    result = RepoRawData(
        repo_data=repo_data,
        commit_activity=commit_activity,
        closed_issues=closed_in_90d,
        releases=releases or [],
        cached=False,
    )
    set_cache(cache_key, result.__dict__)
    return result
