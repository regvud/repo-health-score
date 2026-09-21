import re

GITHUB_REPO_URL: re.Pattern[str] = re.compile(r"https?://github\.com/([^/]+)/([^/\s?#]+)")
