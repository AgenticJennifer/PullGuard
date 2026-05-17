from __future__ import annotations
import asyncio
import argparse
import uvicorn
from pullguard.config import PullGuardConfig
from pullguard.director import Director
from pullguard.github import GitHubClient


async def analyze_repo(repo: str, pr_number: int, config_path: str = ".github/pullguard.yml", dry_run: bool = False):
    config = PullGuardConfig.from_file(config_path)
    github = GitHubClient()
    pr = await github.get_pr(repo, pr_number)
    director = Director(config)
    result = await director.analyze(pr)
    return result


async def analyze_repo_cli(repo: str, pr_number: int, dry_run: bool = False):
    result = await analyze_repo(repo, pr_number, dry_run=dry_run)
    if result is None:
        print("PR skipped (below analysis threshold)")
        return
    from rich.console import Console
    from rich.table import Table
    console = Console()

    table = Table(title=f"PullGuard Analysis — PR #{pr_number}")
    table.add_column("Dimension", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Verdict", style="yellow")
    table.add_column("Confidence", style="magenta")

    if result.slop:
        table.add_row("Slop Detection", str(result.slop.score), result.slop.category.value, result.slop.confidence)
    if result.architecture:
        arch_verdict = "aligned" if result.architecture.passed else "violations"
        table.add_row("Architecture", str(result.architecture.score), arch_verdict, result.architecture.confidence)

    table.add_row("Flagged", "", "[red]YES[/red]" if result.flagged else "[green]No[/green]")
    console.print(table)

    if dry_run and result.comment:
        from rich.panel import Panel
        console.print(Panel(result.comment.body, title="[yellow][DRY RUN] Proposed PR Comment[/yellow]", border_style="yellow"))
        console.print(f"[yellow][DRY RUN] Would post comment to PR #{pr_number} in {repo}[/yellow]")
        raise SystemExit(1 if result.flagged else 0)


def cli():
    parser = argparse.ArgumentParser(description="PullGuard — Anti-Slop PR Sentinel")
    sub = parser.add_subparsers(dest="command")

    analyze = sub.add_parser("analyze", help="Analyze a PR")
    analyze.add_argument("repo", help="Repository (owner/name)")
    analyze.add_argument("pr", type=int, help="PR number")
    analyze.add_argument("--dry-run", action="store_true", help="Preview comment without posting")

    serve = sub.add_parser("serve", help="Run webhook server")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "analyze":
        asyncio.run(analyze_repo_cli(args.repo, args.pr, dry_run=args.dry_run))
    elif args.command == "serve":
        uvicorn.run("pullguard.webhook:app", host=args.host, port=args.port)
    else:
        parser.print_help()
