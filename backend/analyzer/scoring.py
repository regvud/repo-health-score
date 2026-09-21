import math
from datetime import datetime, timezone
from typing import Any

from .schemas import HealthReportSchema, RepoMetaSchema, RepoRawData, SignalResult, SignalSchema


class ScoreCalculator:
    @staticmethod
    def _round10(value: float) -> int:
        return round(value / 10) * 10

    WEIGHTS: dict[str, float] = {
        "responsiveness": 0.30,
        "recency": 0.15,
        "momentum": 0.30,
        "popularity": 0.25,
    }

    LABELS: dict[str, str] = {
        "responsiveness": "Issue responsiveness",
        "recency": "Last commit",
        "momentum": "Commit momentum",
        "popularity": "Popularity",
    }

    def compute(self, raw: RepoRawData) -> HealthReportSchema:
        repo = raw.repo_data

        signals = {
            "responsiveness": self._score_responsiveness(raw.closed_issues, repo.get("open_issues_count", 0)),
            "recency": self._score_recency(repo["pushed_at"]),
            "momentum": self._score_momentum(raw.commit_activity),
            "popularity": self._score_popularity(
                repo.get("stargazers_count", 0),
                repo.get("forks_count", 0),
                raw.releases,
            ),
        }

        weighted_sum = 0.0
        active_weight = 0.0
        for name, weight in self.WEIGHTS.items():
            if signals[name].score is not None:
                weighted_sum += signals[name].score * weight
                active_weight += weight

        final_score = self._round10(weighted_sum / active_weight) if active_weight > 0 else 0

        signal_schemas = [
            SignalSchema(
                name=name,
                label=self.LABELS[name],
                weight=int(self.WEIGHTS[name] * 100),
                score=signal.score,
                value=signal.value,
                status=signal.status,
            )
            for name, signal in signals.items()
        ]

        return HealthReportSchema(
            repo=repo["full_name"],
            score=final_score,
            signals=signal_schemas,
            meta=RepoMetaSchema(
                stars=repo.get("stargazers_count"),
                forks=repo.get("forks_count"),
                open_issues=repo.get("open_issues_count"),
                description=repo.get("description"),
                cached=raw.cached,
            ),
        )

    def _score_responsiveness(self, closed_issues: list[dict[str, Any]], open_issues_count: int) -> SignalResult:
        closed = len(closed_issues)

        if closed == 0 and open_issues_count == 0:
            return SignalResult(score=50, value="No issues tracked", status="neutral")

        # Popular repos naturally accumulate many open issues — score the close/open
        # ratio leniently, then reward high absolute closure volume separately.
        ratio = closed / max(1, open_issues_count)

        if ratio >= 1.0:
            ratio_score = 100
        elif ratio >= 0.3:
            ratio_score = 80
        elif ratio >= 0.1:
            ratio_score = 60
        elif ratio >= 0.05:
            ratio_score = 40
        else:
            ratio_score = 20

        # Volume bonus: closing 100+ issues in 90 days signals an actively maintained project
        # (per_page=100 cap means hitting it implies even higher real activity)
        if closed >= 100:
            volume_bonus = 20
        elif closed >= 50:
            volume_bonus = 10
        elif closed >= 20:
            volume_bonus = 5
        else:
            volume_bonus = 0

        raw = min(100, ratio_score + volume_bonus)

        return SignalResult(
            score=self._round10(raw),
            value=f"{closed} issues closed in 90d · {open_issues_count} open",
            status="good" if raw >= 60 else "warning" if raw >= 40 else "bad",
        )

    def _score_recency(self, pushed_at: str) -> SignalResult:
        last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - last_push).days

        if days < 7:
            raw, label = 100, f"{days}d ago"
        elif days < 30:
            raw, label = 80, f"{days}d ago"
        elif days < 90:
            raw, label = 60, f"{days}d ago"
        elif days < 180:
            raw, label = 40, f"{days}d ago"
        elif days < 365:
            raw, label = 20, f"{days}d ago"
        else:
            raw, label = 0, f"{days // 30} months ago"

        return SignalResult(
            score=self._round10(raw),
            value=f"Last commit {label}",
            status="good" if raw >= 60 else "warning" if raw >= 40 else "bad",
        )

    def _score_momentum(self, commit_activity: list[dict[str, Any]] | None) -> SignalResult:
        if not commit_activity or len(commit_activity) < 26:
            return SignalResult(score=None, value="Data unavailable", status="neutral")

        recent = sum(w["total"] for w in commit_activity[-13:])
        prior = sum(w["total"] for w in commit_activity[-26:-13])

        if recent == 0 and prior == 0:
            return SignalResult(score=self._round10(30), value="No commits in 6 months", status="bad")

        if prior == 0:
            return SignalResult(score=self._round10(80), value="New project with recent activity", status="good")

        ratio = recent / prior

        if ratio >= 1.2:
            raw, label = 100, f"up {int((ratio - 1) * 100)}% vs prior quarter"
        elif ratio >= 0.8:
            raw, label = 80, "stable"
        elif ratio >= 0.5:
            raw, label = 60, f"down {int((1 - ratio) * 100)}% vs prior quarter"
        elif ratio >= 0.2:
            raw, label = 40, f"down {int((1 - ratio) * 100)}% vs prior quarter"
        else:
            raw, label = 20, f"down {int((1 - ratio) * 100)}% vs prior quarter"

        return SignalResult(
            score=self._round10(raw),
            value=f"Commit trend {label}",
            status="good" if raw >= 60 else "warning" if raw >= 40 else "bad",
        )

    def _score_popularity(self, stars: int, forks: int, releases: list[dict[str, Any]]) -> SignalResult:
        total_downloads = sum(
            asset.get("download_count", 0)
            for release in releases
            for asset in release.get("assets", [])
        )

        # log10 scale: 1→0, 10→25, 100→50, 1000→75, 10000→100
        combined = stars + (forks * 2) + (total_downloads // 100)
        raw = min(100, math.log10(max(1, combined)) / 4 * 100) if combined > 0 else 0

        parts = [f"{stars:,} stars", f"{forks:,} forks"]
        if total_downloads > 0:
            parts.append(f"{total_downloads:,} downloads")

        return SignalResult(
            score=self._round10(raw),
            value=", ".join(parts),
            status="good" if raw >= 60 else "warning" if raw >= 30 else "bad",
        )
