# Contributing to PullGuard

## Development Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/AgenticJennifer/PullGuard.git
   cd PullGuard
   ```

2. **Install uv** (if not installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Sync dependencies:**
   ```bash
   uv sync
   ```

4. **Run tests:**
   ```bash
   uv run pytest tests/ -v
   ```

## Code Style

- We use `ruff` for linting. Run `uv run ruff check .` before committing.
- Python 3.11+ type annotations required.
- Line length: 100 characters.

## Branch Naming

- `feat/<description>` for new features
- `fix/<description>` for bug fixes
- `docs/<description>` for documentation changes

## PR Process

1. Create a branch from `main`.
2. Make your changes.
3. Add or update tests.
4. Run `uv run pytest tests/ -v` to verify all tests pass.
5. Open a pull request against `main`.

## Architecture Overview

PullGuard uses a three-agent architecture:

- **SlopClassifier** — Detects AI-generated "slop" code by analyzing PRs for hallucinated APIs, boilerplate, and missing error handling.
- **ArchitectureAuditor** — Checks if the PR respects documented project architecture patterns.
- **CommunityLiaison** — Generates a constructive, human-friendly PR review comment.

A **Director** orchestrates all three agents concurrently and computes per-dimension scores.
