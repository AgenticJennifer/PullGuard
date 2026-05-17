from __future__ import annotations
import asyncio
import logging
import os
import time
from typing import Any
import httpx
from pullguard.models import PullRequest, PRFile

logger = logging.getLogger("pullguard.github")


class RateLimitExhausted(Exception):
    def __init__(self, repo: str, pr_number: int, retries: int):
        self.repo = repo
        self.pr_number = pr_number
        self.retries = retries
        super().__init__(f"Rate limit exhausted after {retries} retries for {repo}#{pr_number}")


class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN") or ""
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "pullguard/0.1.0",
        }

    async def get_pr(self, repo: str, pr_number: int) -> PullRequest:
        repo = repo.strip("/")
        async with httpx.AsyncClient() as client:
            pr_resp = await self._call_with_retry(
                client.get,
                f"{self.BASE}/repos/{repo}/pulls/{pr_number}",
            )

            files_resp = await self._call_with_retry(
                client.get,
                f"{self.BASE}/repos/{repo}/pulls/{pr_number}/files",
                params={"per_page": 100},
            )

        pr_data = pr_resp.json()
        files_data = files_resp.json()

        files = [
            PRFile(
                filename=f["filename"],
                status=f["status"],
                additions=f.get("additions", 0),
                deletions=f.get("deletions", 0),
                patch=f.get("patch"),
                raw_url=f.get("contents_url"),
            )
            for f in files_data
        ]

        return PullRequest(
            number=pr_data["number"],
            title=pr_data["title"],
            body=pr_data.get("body"),
            author=pr_data["user"]["login"],
            base_branch=pr_data["base"]["ref"],
            head_sha=pr_data["head"]["sha"],
            files=files,
            url=pr_data["html_url"],
        )

    async def post_review(
        self, repo: str, pr_number: int, body: str, event: str = "COMMENT"
    ) -> dict[str, Any]:
        repo = repo.strip("/")
        async with httpx.AsyncClient() as client:
            resp = await self._call_with_retry(
                client.post,
                f"{self.BASE}/repos/{repo}/pulls/{pr_number}/reviews",
                json={"body": body, "event": event},
            )
            return resp.json()

    async def create_issue_comment(
        self, repo: str, pr_number: int, body: str
    ) -> dict[str, Any]:
        repo = repo.strip("/")
        async with httpx.AsyncClient() as client:
            resp = await self._call_with_retry(
                client.post,
                f"{self.BASE}/repos/{repo}/issues/{pr_number}/comments",
                json={"body": body},
            )
            return resp.json()

    async def _call_with_retry(self, method, url, max_retries=5, **kwargs):
        last_exc = None
        for attempt in range(max_retries):
            start = time.monotonic()
            try:
                resp = await method(url, headers=self.headers, **kwargs)
                elapsed = (time.monotonic() - start) * 1000
                logger.info(
                    "github_api_call",
                    extra={
                        "method": method.__name__,
                        "url": url,
                        "status_code": resp.status_code,
                        "latency_ms": round(elapsed),
                        "retry_count": attempt,
                    },
                )
                if resp.status_code in (403, 429):
                    retry_after = self._parse_retry_after(resp)
                    wait = min(retry_after, 60)
                    logger.warning(
                        "rate_limit_hit",
                        extra={"url": url, "retry_after": wait, "attempt": attempt},
                    )
                    await asyncio.sleep(wait)
                    continue

                if resp.status_code >= 500 and attempt < 2:
                    await asyncio.sleep(1)
                    continue

                resp.raise_for_status()
                return resp

            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                elapsed = (time.monotonic() - start) * 1000
                logger.warning(
                    "github_api_error",
                    extra={
                        "url": url,
                        "error": str(exc),
                        "latency_ms": round(elapsed),
                        "attempt": attempt,
                    },
                )
                if attempt < max_retries - 1:
                    wait = min(2 ** attempt, 60)
                    await asyncio.sleep(wait)
                    continue
                raise

        raise RateLimitExhausted(
            repo=url.split("/repos/")[1].split("/pulls")[0].split("/issues")[0] if "/repos/" in url else "unknown",
            pr_number=0,
            retries=max_retries,
        )

    def _parse_retry_after(self, resp: httpx.Response) -> int:
        raw = resp.headers.get("Retry-After")
        if raw:
            try:
                return int(raw)
            except ValueError:
                pass
        return 5
