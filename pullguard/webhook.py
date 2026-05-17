from __future__ import annotations
import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException
from pullguard.director import Director
from pullguard.config import PullGuardConfig
from pullguard.github import GitHubClient

app = FastAPI(title="PullGuard")
webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")


@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")

    if webhook_secret:
        expected = "sha256=" + hmac.new(
            webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise HTTPException(403, "Invalid signature")

    event = request.headers.get("X-GitHub-Event", "")
    if event != "pull_request":
        return {"status": "skipped", "reason": f"unhandled event: {event}"}

    payload = await request.json()
    action = payload.get("action", "")
    if action not in ("opened", "synchronize"):
        return {"status": "skipped", "reason": f"unhandled action: {action}"}

    repo_full_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]

    config = PullGuardConfig()
    github = GitHubClient()
    pr = await github.get_pr(repo_full_name, pr_number)

    director = Director(config)
    result = await director.analyze(pr)

    if result.comment:
        await github.create_issue_comment(repo_full_name, pr_number, result.comment.body)

    return {
        "status": "ok",
        "pr_number": pr_number,
        "overall_score": result.overall_score,
        "slop_score": result.slop.score if result.slop else None,
        "arch_score": result.architecture.score if result.architecture else None,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
