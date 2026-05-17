# PullGuard — The Anti-Slop PR Sentinel

A GitHub-integrated LLM agent that reviews incoming PRs, detects AI-generated "slop," scores code quality, and checks architectural alignment — before a human ever sees the diff.

## How It Works

PullGuard runs three agent roles on every new or updated PR:

| Agent | Role |
|-------|------|
| **Slop Classifier** | LLM analysis for hallucinated APIs, plausible-but-wrong logic, excessive boilerplate, missing error handling, and inconsistent style. Outputs a 0–100 quality score. |
| **Architecture Auditor** | Checks the PR diff against your project's docs (ARCHITECTURE.md, docs/). Flags violations of existing patterns, module boundaries, and unnecessary complexity. |
| **Community Liaison** | Generates a human-friendly PR comment summarising findings with a constructive tone. Maintainers stay informed; contributors get actionable feedback. |

A **Director of Engineering** orchestrator dispatches the Slop Classifier and Architecture Auditor in parallel, averages their scores, and hands results to the Community Liaison for the final comment.

## Quick Start

### CLI (analyze a PR)

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_..."

# Analyze a PR
pullguard analyze owner/repo 42
```

Outputs a rich table with scores and reasoning.

### Webhook server (automated on PR events)

```bash
# Set env vars
export GITHUB_TOKEN="ghp_..."
export GITHUB_WEBHOOK_SECRET="your-secret"

# Start the server
pullguard serve --port 8000
```

Configure your GitHub repo's webhook to `https://your-server:8000/webhook` with content type `application/json` and the secret above. PullGuard automatically comments on every newly opened or updated PR.

## Per-Repo Configuration

Drop a `.github/pullguard.yml` in your repo:

```yaml
version: 1
analysis:
  min_score: 50           # below this, the PR is flagged
  max_files_to_sample: 20
llm:
  model: "gemini-2.0-flash"
  temperature: 0.3
slop_classifier:
  enabled: true
  thresholds:
    suspicious: 40
    likely_slop: 25
architect:
  enabled: true
  required_dirs:
    - docs/
    - ARCHITECTURE.md
community:
  tone: "constructive"    # constructive | firm | praise
  mention_maintainer_on_score_below: 30
```

## Development

```bash
uv sync             # install dependencies
uv run pytest       # run tests (22 tests)
uv run pytest -v    # verbose
```

## Tech Stack

**Python 3.11+** · FastAPI · httpx · Pydantic · Google Gemini · Rich · PyYAML
