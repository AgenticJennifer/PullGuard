import pytest
from unittest.mock import AsyncMock, patch
from pullguard.config import PullGuardConfig
from pullguard.models import PullRequest, PRFile, SlopAnalysis, SlopCategory, CommentDraft, ArchitectureAudit
from pullguard.director import Director


@pytest.mark.asyncio
async def test_director_returns_both_scores():
    config = PullGuardConfig()
    director = Director(config)

    pr = PullRequest(
        number=42,
        title="Fix login bug",
        author="testuser",
        base_branch="main",
        head_sha="abc123",
        files=[PRFile(filename="src/main.py", status="modified", additions=10, deletions=2)],
        url="https://github.com/owner/repo/pull/42",
    )

    with patch.object(director.slop_classifier, "run", new=AsyncMock(return_value=SlopAnalysis(
        score=80, category=SlopCategory.REAL, reasoning="clean code"
    ))):
        with patch.object(director.architect, "run", new=AsyncMock(return_value=ArchitectureAudit(
            passed=True, score=90, findings=[], project_docs_used=[]
        ))):
            with patch.object(director.liaison, "run", new=AsyncMock(return_value=CommentDraft(
                body="Great PR!", tone="praise", include_summary=True, include_score=True
            ))):
                result = await director.analyze(pr)

    assert result is not None
    assert result.slop.score == 80
    assert result.architecture.score == 90
    assert result.flagged is False
    assert result.comment is not None


@pytest.mark.asyncio
async def test_director_flags_low_scores():
    config = PullGuardConfig()
    director = Director(config)

    pr = PullRequest(
        number=43,
        title="Bad code",
        author="testuser",
        base_branch="main",
        head_sha="abc123",
        files=[PRFile(filename="src/main.py", status="modified", additions=100, deletions=0)],
        url="https://github.com/owner/repo/pull/43",
    )

    with patch.object(director.slop_classifier, "run", new=AsyncMock(return_value=SlopAnalysis(
        score=15, category=SlopCategory.SLOP, reasoning="hallucinated APIs"
    ))):
        with patch.object(director.architect, "run", new=AsyncMock(return_value=ArchitectureAudit(
            passed=False, score=20, findings=[], project_docs_used=[]
        ))):
            with patch.object(director.liaison, "run", new=AsyncMock(return_value=CommentDraft(
                body="Needs work", tone="constructive", include_summary=True, include_score=True
            ))):
                result = await director.analyze(pr)

    assert result is not None
    assert result.flagged is True
