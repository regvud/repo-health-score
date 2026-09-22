# Repository Health Score

A tool for evaluating open-source dependencies before you commit to them. Paste a GitHub URL, get a structured score with the reasoning behind it.

**Live demo:** https://believable-appreciation-production.up.railway.app

---

## What does "will we regret this" mean?

Regret, in practice, means one of three things: the project goes dark and stops receiving fixes, it turns out to be unresponsive to real-world issues, or it was never proven at scale to begin with.

That framing led to four signals:

| Signal | Weight | What it measures |
|---|---|---|
| **Issue responsiveness** | 30% | Issues closed in the last 90 days vs. open backlog — a proxy for whether maintainers actually engage with the community |
| **Commit momentum** | 30% | Commit volume in the last 13 weeks vs. the 13 weeks before — catches projects that are quietly winding down |
| **Popularity** | 25% | Stars, forks, and release download count on a log scale — evidence that others have bet on this too |
| **Last commit** | 15% | How recently anything was pushed — a sanity check, weighted lowest because a stable library can go months without commits legitimately |

Responsiveness and momentum are weighted equally and highest because they measure *behaviour*, not accumulated reputation. A project with 10k stars that stopped merging PRs two years ago is exactly the kind of thing this tool is meant to surface.

---

## What was deliberately cut

**Contributor analysis.** Bus-factor (how many people account for 80% of commits) is probably the single most predictive signal for abandonment risk. It's not here because the contributors endpoint requires iterating commits in a way that's slow and burns rate limit budget fast.

**License and dependency checks.** Relevant for the "will we regret this" question legally, but a different kind of problem — better handled by dedicated tools like `license-checker` or Snyk.

**PR merge time.** A cleaner responsiveness signal than closed-issue ratio, but the search API endpoint needed for it counts against a separate rate limit bucket.

**Historical trend charts.** Commit activity data is already fetched (it's what momentum scoring uses), so rendering it as a sparkline would be low-effort. Cut for time, not for difficulty.

**Authentication / rate limit handling on the frontend.** The backend distinguishes 429s and returns a clear error. The frontend shows it. A `GITHUB_TOKEN` on the server raises the limit from 60 to 5,000 req/hr, which is enough for a shared deployment.

---

## Stack decisions worth noting

**Django async view + httpx.** The four GitHub API calls (repo metadata, commit activity, closed issues, releases) run concurrently via `asyncio.gather`. On an uncached request this saves roughly 2–3 seconds vs. sequential calls. Django's async support is stable enough for this use case without reaching for FastAPI.

**Redis cache (5-minute TTL).** Caching avoids burning rate limit on repeated lookups of the same repo and makes the UI feel fast on the second hit.

**Score rounded to nearest 10.** Displaying 73 vs. 74 implies a precision the model doesn't have. Rounding to the nearest 10 is honest about the fuzziness.

---

## How AI tools were used

Claude Code (Anthropic's CLI) was used throughout: scaffolding the Django project structure, writing the initial scoring logic, TypeScript interfaces, and iterating on the weighting model. The signal design and weight choices were mine — I used the AI to implement them quickly once I'd decided what to measure and why, and to debug deployment issues on Railway.

The parts that required genuine judgment — what signals matter, how to weight them, what to cut — weren't delegated.

---

## Running locally

**Requirements:** Docker and Docker Compose.

```bash
cp .env.example .env
# optionally add a GITHUB_TOKEN to .env to raise the rate limit
docker compose up --build
```

Frontend: http://localhost:5173  
Backend: http://localhost:8000

---

## What's next

1. **Contributor bus-factor** — the missing signal. Worth the rate-limit cost for a production tool.
2. **Sparkline for commit trend** — the data is already fetched, just not rendered.
3. **Comparison mode** — score two repos side by side before choosing between them.
4. **Webhook / CI integration** — post a score as a PR comment when a new dependency is added to `package.json` or `requirements.txt`.
