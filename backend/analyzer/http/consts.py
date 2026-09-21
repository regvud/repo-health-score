GITHUB_API_BASE: str = "https://api.github.com"
GITHUB_API_VERSION: str = "2022-11-28"

LOOKBACK_DAYS: int = 90
ISSUES_PER_PAGE: int = 100
RELEASES_PER_PAGE: int = 10
STATS_RETRY_DELAY: int = 2
REQUEST_TIMEOUT: int = 15

BASE_HEADERS: dict[str, str] = {
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": GITHUB_API_VERSION,
}
