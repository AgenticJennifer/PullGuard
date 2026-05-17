from __future__ import annotations
import os
from typing import Any
import httpx
from pullguard.models import PullRequest, PRFile


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
            pr_resp = await client.get(
                f"{self.BASE}/repos/{repo}/pulls/{pr_number}",
                headers=self.headers,
            )
            pr_resp.raise_for_status()
            pr_data = pr_resp.json()

            files_resp = await client.get(
                f"{self.BASE}/repos/{repo}/pulls/{pr_number}/files",
                headers=self.headers,
                params={"per_page": 100},
            )
            files_resp.raise_for_status()
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
            resp = await client.post(
                f"{self.BASE}/repos/{repo}/pulls/{pr_number}/reviews",
                headers=self.headers,
                json={"body": body, "event": event},
            )
            resp.raise_for_status()
            return resp.json()

    async def create_issue_comment(
        self, repo: str, pr_number: int, body: str
    ) -> dict[str, Any]:
        repo = repo.strip("/")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE}/repos/{repo}/issues/{pr_number}/comments",
                headers=self.headers,
                json={"body": body},
            )
            resp.raise_for_status()
            return resp.json()
