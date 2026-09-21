from dataclasses import asdict

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from .exceptions import GitHubNotFoundError, GitHubRateLimitError
from .http import fetch_repo_data, parse_github_url
from .scoring import ScoreCalculator

calculator = ScoreCalculator()


class AnalyzeView(View):
    async def get(self, request: HttpRequest) -> JsonResponse:
        url = request.GET.get("url", "").strip()
        if not url:
            return JsonResponse({"error": "url parameter is required"}, status=400)

        try:
            owner, repo = parse_github_url(url)
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        try:
            raw = await fetch_repo_data(owner, repo)
        except GitHubNotFoundError:
            return JsonResponse({"error": f"Repository not found: {owner}/{repo}"}, status=404)
        except GitHubRateLimitError:
            return JsonResponse(
                {"error": "GitHub API rate limit exceeded. Try again in an hour, or add a GITHUB_TOKEN."},
                status=429,
            )
        except Exception:
            return JsonResponse({"error": "Failed to fetch repository data from GitHub"}, status=502)

        return JsonResponse(asdict(calculator.compute(raw)))
