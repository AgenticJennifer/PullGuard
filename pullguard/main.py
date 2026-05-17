from __future__ import annotations
import asyncio
import argparse
import uvicorn
from pullguard.config import PullGuardConfig
from pullguard.director import Director
from pullguard.github import GitHubClient


async def analyze_repo(repo: str, pr_number: int, config_path: str = ".github/pullguard.yml"):
    config = PullGuardConfig.from_file(config_path)
    github = GitHubClient()
    pr = await github.get_pr(repo, pr_number)
    director = Director(config)
    result = await director.analyze(pr)
    return result


async def analyze_repo_cli(repo: str, pr_number: int):
    result = await analyze_repo(repo, pr_number)
    from rich.console import Console
    from rich.table import Table
    console = Console()

    table = Table(title=f"PullGuard Analysis — PR #{pr_number}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Overall Score", str(result.overall_score))
    if result.slop:
        table.add_row("Slop Score", f"{result.slop.score}/100 ({result.slop.category.value})")
        table.add_row("Slop Reasoning", result.slop.reasoning[:100])
    if result.architecture:
        table.add_row("Arch Score", f"{result.architecture.score}/100")
        table.add_row("Arch Passed", str(result.architecture.passed))
    console.print(table)


def cli():
    parser = argparse.ArgumentParser(description="PullGuard — Anti-Slop PR Sentinel")
    sub = parser.add_subparsers(dest="command")

    analyze = sub.add_parser("analyze", help="Analyze a PR")
    analyze.add_argument("repo", help="Repository (owner/name)")
    analyze.add_argument("pr", type=int, help="PR number")

    serve = sub.add_parser("serve", help="Run webhook server")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "analyze":
        asyncio.run(analyze_repo_cli(args.repo, args.pr))
    elif args.command == "serve":
        uvicorn.run("pullguard.webhook:app", host=args.host, port=args.port)
    else:
        parser.print_help()
