from __future__ import annotations
import logging
from fastapi import FastAPI, Request, Response
from pullguard.logging import configure_logging
from pullguard.security import configure_webhook_secret, verify_signature
from pullguard.director import Director
from pullguard.config import PullGuardConfig
from pullguard.github import GitHubClient
from pullguard.dashboard import router as dashboard_router

configure_logging("server")
logger = logging.getLogger("pullguard.webhook")
app = FastAPI(title="PullGuard")
app.include_router(dashboard_router)
configure_webhook_secret()


@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(body, sig):
        return Response(status_code=401)

    event = request.headers.get("X-GitHub-Event", "")
    if event == "pull_request":
        return await _handle_pr_event(body, request)
    if event == "issue_comment":
        return await _handle_comment_event(body, request)

    return {"status": "skipped", "reason": f"unhandled event: {event}"}


async def _handle_pr_event(body: bytes, request: Request) -> dict:
    payload = await request.json()
    action = payload.get("action", "")
    if action not in ("opened", "synchronize"):
        return {"status": "skipped", "reason": f"unhandled action: {action}"}

    return await _run_analysis(payload)


async def _handle_comment_event(body: bytes, request: Request) -> dict:
    payload = await request.json()
    comment_body = payload.get("comment", {}).get("body", "")
    is_recheck = comment_body.strip().lower().startswith("/pullguard recheck")
    if not is_recheck:
        return {"status": "skipped", "reason": "not a recheck command"}

    has_pr = payload.get("issue", {}).get("pull_request")
    if not has_pr:
        return {"status": "skipped", "reason": "comment not on a PR"}

    return await _run_analysis(payload)


async def _run_analysis(payload: dict) -> dict:
    repo_full_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]

    config = PullGuardConfig()
    github = GitHubClient()
    pr = await github.get_pr(repo_full_name, pr_number)

    director = Director(config)
    result = await director.analyze(pr)

    if result and result.comment:
        await github.create_issue_comment(repo_full_name, pr_number, result.comment.body)

    slop_score = result.slop.score if result and result.slop else None
    arch_score = result.architecture.score if result and result.architecture else None

    return {
        "status": "ok",
        "pr_number": pr_number,
        "slop_score": slop_score,
        "arch_score": arch_score,
        "flagged": result.flagged if result else False,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
